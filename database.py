"""
Database module for Neon PostgreSQL integration
"""
import os
import psycopg2
from psycopg2.extras import RealDictCursor
from typing import Dict, Any, List, Optional
import logging
import json

logger = logging.getLogger(__name__)

# Get database URL from environment
DATABASE_URL = os.environ.get("NETLIFY_DATABASE_URL") or os.environ.get("DATABASE_URL")

def get_db_connection():
    """Get database connection"""
    if not DATABASE_URL:
        logger.warning("No DATABASE_URL found, database operations will fail")
        return None
    
    try:
        conn = psycopg2.connect(DATABASE_URL)
        return conn
    except Exception as e:
        logger.error(f"Error connecting to database: {e}")
        return None

def init_database():
    """Initialize database tables"""
    conn = get_db_connection()
    if not conn:
        logger.error("Cannot initialize database: no connection")
        return False
    
    try:
        cur = conn.cursor()
        
        # Create config table
        cur.execute("""
            CREATE TABLE IF NOT EXISTS config (
                id SERIAL PRIMARY KEY,
                key VARCHAR(255) UNIQUE NOT NULL,
                value TEXT NOT NULL,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Create banned_accounts table
        cur.execute("""
            CREATE TABLE IF NOT EXISTS banned_accounts (
                id SERIAL PRIMARY KEY,
                player_id VARCHAR(255) UNIQUE NOT NULL,
                player_name VARCHAR(255),
                hwid TEXT,
                ip_address VARCHAR(45),
                reason TEXT,
                ban_duration_hours INTEGER,
                banned_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                expires_at TIMESTAMP,
                account_data JSONB
            )
        """)
        
        # Create allowed_accounts table
        cur.execute("""
            CREATE TABLE IF NOT EXISTS allowed_accounts (
                id SERIAL PRIMARY KEY,
                player_id VARCHAR(255) UNIQUE NOT NULL,
                player_name VARCHAR(255),
                added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                added_by VARCHAR(255),
                account_data JSONB
            )
        """)
        
        conn.commit()
        cur.close()
        conn.close()
        logger.info("Database initialized successfully")
        return True
    except Exception as e:
        logger.error(f"Error initializing database: {e}")
        if conn:
            conn.rollback()
            conn.close()
        return False

def load_config_from_db() -> Dict[str, Any]:
    """Load configuration from database"""
    conn = get_db_connection()
    if not conn:
        return {}
    
    try:
        cur = conn.cursor(cursor_factory=RealDictCursor)
        cur.execute("SELECT key, value FROM config")
        rows = cur.fetchall()
        cur.close()
        conn.close()
        
        config = {}
        for row in rows:
            try:
                # Try to parse JSON, fallback to string
                config[row['key']] = json.loads(row['value'])
            except:
                config[row['key']] = row['value']
        
        return config
    except Exception as e:
        logger.error(f"Error loading config from database: {e}")
        if conn:
            conn.close()
        return {}

def save_config_to_db(config: Dict[str, Any]) -> bool:
    """Save configuration to database"""
    conn = get_db_connection()
    if not conn:
        return False
    
    try:
        cur = conn.cursor()
        for key, value in config.items():
            # Convert value to JSON string
            value_str = json.dumps(value) if not isinstance(value, str) else value
            cur.execute("""
                INSERT INTO config (key, value, updated_at)
                VALUES (%s, %s, CURRENT_TIMESTAMP)
                ON CONFLICT (key) DO UPDATE
                SET value = EXCLUDED.value, updated_at = CURRENT_TIMESTAMP
            """, (key, value_str))
        
        conn.commit()
        cur.close()
        conn.close()
        return True
    except Exception as e:
        logger.error(f"Error saving config to database: {e}")
        if conn:
            conn.rollback()
            conn.close()
        return False

def load_banned_accounts_from_db() -> List[Dict[str, Any]]:
    """Load banned accounts from database"""
    conn = get_db_connection()
    if not conn:
        return []
    
    try:
        cur = conn.cursor(cursor_factory=RealDictCursor)
        cur.execute("""
            SELECT 
                player_id as "playerId",
                player_name as "playerName",
                hwid,
                ip_address as "ipAddress",
                reason,
                ban_duration_hours as "banDurationHours",
                banned_at as "bannedAt",
                expires_at as "expiresAt",
                account_data as "accountData"
            FROM banned_accounts
            ORDER BY banned_at DESC
        """)
        rows = cur.fetchall()
        cur.close()
        conn.close()
        
        accounts = []
        for row in rows:
            account = dict(row)
            # Convert timestamps to strings
            if account.get('bannedAt'):
                account['bannedAt'] = account['bannedAt'].isoformat()
            if account.get('expiresAt'):
                account['expiresAt'] = account['expiresAt'].isoformat()
            accounts.append(account)
        
        return accounts
    except Exception as e:
        logger.error(f"Error loading banned accounts from database: {e}")
        if conn:
            conn.close()
        return []

def save_banned_account_to_db(account: Dict[str, Any]) -> bool:
    """Save a banned account to database"""
    conn = get_db_connection()
    if not conn:
        return False
    
    try:
        cur = conn.cursor()
        
        player_id = account.get("playerId")
        player_name = account.get("playerName")
        hwid = account.get("hwid")
        ip_address = account.get("ipAddress")
        reason = account.get("reason")
        ban_duration_hours = account.get("banDurationHours", 336)
        
        # Calculate expires_at
        expires_at = None
        if ban_duration_hours and ban_duration_hours > 0:
            from datetime import datetime, timedelta
            expires_at = datetime.utcnow() + timedelta(hours=ban_duration_hours)
        
        account_data = json.dumps(account.get("accountData", {}))
        
        cur.execute("""
            INSERT INTO banned_accounts (
                player_id, player_name, hwid, ip_address, reason,
                ban_duration_hours, expires_at, account_data
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s::jsonb)
            ON CONFLICT (player_id) DO UPDATE
            SET 
                player_name = EXCLUDED.player_name,
                hwid = EXCLUDED.hwid,
                ip_address = EXCLUDED.ip_address,
                reason = EXCLUDED.reason,
                ban_duration_hours = EXCLUDED.ban_duration_hours,
                expires_at = EXCLUDED.expires_at,
                account_data = EXCLUDED.account_data
        """, (player_id, player_name, hwid, ip_address, reason, ban_duration_hours, expires_at, account_data))
        
        conn.commit()
        cur.close()
        conn.close()
        return True
    except Exception as e:
        logger.error(f"Error saving banned account to database: {e}")
        if conn:
            conn.rollback()
            conn.close()
        return False

def load_allowed_accounts_from_db() -> List[Dict[str, Any]]:
    """Load allowed accounts from database"""
    conn = get_db_connection()
    if not conn:
        return []
    
    try:
        cur = conn.cursor(cursor_factory=RealDictCursor)
        cur.execute("""
            SELECT 
                player_id as "playerId",
                player_name as "playerName",
                added_at as "addedAt",
                added_by as "addedBy",
                account_data as "accountData"
            FROM allowed_accounts
            ORDER BY added_at DESC
        """)
        rows = cur.fetchall()
        cur.close()
        conn.close()
        
        accounts = []
        for row in rows:
            account = dict(row)
            if account.get('addedAt'):
                account['addedAt'] = account['addedAt'].isoformat()
            accounts.append(account)
        
        return accounts
    except Exception as e:
        logger.error(f"Error loading allowed accounts from database: {e}")
        if conn:
            conn.close()
        return []

def save_allowed_accounts_to_db(accounts: List[Dict[str, Any]]) -> bool:
    """Save allowed accounts to database"""
    conn = get_db_connection()
    if not conn:
        return False
    
    try:
        cur = conn.cursor()
        
        # Clear existing accounts
        cur.execute("DELETE FROM allowed_accounts")
        
        # Insert new accounts
        for account in accounts:
            player_id = account.get("playerId")
            player_name = account.get("playerName")
            added_by = account.get("addedBy", "system")
            account_data = json.dumps(account.get("accountData", {}))
            
            cur.execute("""
                INSERT INTO allowed_accounts (player_id, player_name, added_by, account_data)
                VALUES (%s, %s, %s, %s::jsonb)
            """, (player_id, player_name, added_by, account_data))
        
        conn.commit()
        cur.close()
        conn.close()
        return True
    except Exception as e:
        logger.error(f"Error saving allowed accounts to database: {e}")
        if conn:
            conn.rollback()
            conn.close()
        return False

def is_account_allowed_in_db(player_id: str) -> bool:
    """Check if account is allowed in database"""
    conn = get_db_connection()
    if not conn:
        return False
    
    try:
        cur = conn.cursor()
        cur.execute("SELECT COUNT(*) FROM allowed_accounts WHERE player_id = %s", (player_id,))
        count = cur.fetchone()[0]
        cur.close()
        conn.close()
        return count > 0
    except Exception as e:
        logger.error(f"Error checking allowed account in database: {e}")
        if conn:
            conn.close()
        return False

def remove_allowed_account_from_db(player_id: str) -> bool:
    """Remove allowed account from database"""
    conn = get_db_connection()
    if not conn:
        return False
    
    try:
        cur = conn.cursor()
        cur.execute("DELETE FROM allowed_accounts WHERE player_id = %s", (player_id,))
        conn.commit()
        cur.close()
        conn.close()
        return True
    except Exception as e:
        logger.error(f"Error removing allowed account from database: {e}")
        if conn:
            conn.rollback()
            conn.close()
        return False

