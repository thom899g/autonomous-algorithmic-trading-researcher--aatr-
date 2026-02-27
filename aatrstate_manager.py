"""
State Management using Firebase Firestore for persistent storage of:
- Trading strategies and their metadata
- Backtesting results
- RL training progress
- Deployment status
- Performance metrics
"""

import logging
from typing import Dict, Any, Optional, List
from datetime import datetime
import json

try:
    import firebase_admin
    from firebase_admin import credentials, firestore
    from google.cloud.firestore_v1 import Client as FirestoreClient
    from google.cloud.exceptions import GoogleCloudError
except ImportError as e:
    logging.error(f"Firebase import error: {e}. Install with: pip install firebase-admin")
    raise

class StateManager:
    """Firebase-based state management with robust error handling"""
    
    def __init__(self, config_path: str = "./config.yaml"):
        """
        Initialize Firebase connection with error handling and validation
        
        Args:
            config_path: Path to configuration file
        """
        self.logger = logging.getLogger(__name__)
        self._client: Optional[FirestoreClient] = None
        
        try:
            # Load config
            import yaml
            with open(config_path, 'r') as f:
                self.config = yaml.safe_load(f)
            
            # Initialize Firebase
            cred_path = self.config.get('firebase', {}).get('credentials_path')
            if not cred_path:
                raise ValueError("Firebase credentials path not specified in config")
            
            # Check if Firebase app already exists
            if not firebase_admin._apps:
                cred = credentials.Certificate(cred_path)
                firebase_admin.initialize_app(cred)
            
            self._client = firestore.client()
            self.logger.info("Firebase Firestore client initialized successfully")
            
            # Initialize collections if they don't exist
            self._ensure_collections_exist()
            
        except FileNotFoundError as e:
            self.logger.error(f"Config file not found: {e}")
            raise
        except ValueError as e:
            self.logger.error(f"Configuration error: {e}")
            raise
        except Exception as e:
            self.logger.error(f"Failed to initialize StateManager: {e}")
            raise
    
    def _ensure_collections_exist(self) -> None:
        """Ensure required collections exist in Firestore"""
        required_collections = [
            'strategies',
            'backtest_results',
            'rl_training_logs',
            'deployment_status',
            'performance_metrics'
        ]
        
        for collection in required_collections:
            try:
                # Create a dummy document to ensure collection exists
                doc_ref = self._client.collection(collection).document('_init')
                doc_ref.set({'initialized_at': datetime.utcnow().isoformat()})
                doc_ref.delete()  # Clean up dummy document
                self.logger.debug(f"Verified collection: {collection}")
            except GoogleCloudError as e:
                self.logger.error(f"Failed to verify collection {collection}: {e}")
                raise
    
    def save_strategy(
        self,
        strategy_id: str,
        strategy_def: Dict[str, Any],
        metadata: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Save a trading strategy definition to Firestore
        
        Args:
            strategy_id: Unique identifier for the strategy
            strategy_def: Strategy definition dictionary
            metadata: Additional metadata (creator, timestamp, etc.)
            
        Returns:
            bool: Success status
        """
        if not self._client:
            self.logger.error("Firestore client not initialized")
            return False
        
        try:
            doc_ref = self._client.collection('strategies').document(strategy_id)
            
            # Prepare document data
            doc_data = {
                'strategy_definition': strategy_def,