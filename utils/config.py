"""
Configuration management
"""

import os
import json
from pathlib import Path
from typing import List, Dict
from utils.logger import setup_logger

logger = setup_logger(__name__)


class Config:
    """Project configuration and directory management"""
    
    def __init__(self, project_name: str):
        self.project_name = project_name
        
        # Base directories
        self.base_dir = Path.cwd()
        self.projects_dir = self.base_dir / "projects"
        self.project_dir = self.projects_dir / project_name
        
        # Project subdirectories
        self.output_dir = self.project_dir / "output"
        self.images_dir = self.project_dir / "images"
        self.scripts_dir = self.project_dir / "scripts"
        self.logs_dir = self.project_dir / "logs"
        
        # Setup logging
        log_file = self.logs_dir / "pipeline.log"
        self.logger = setup_logger(__name__, str(log_file))
    
    def setup_directories(self):
        """Create all necessary directories"""
        directories = [
            self.project_dir,
            self.output_dir,
            self.images_dir,
            self.scripts_dir,
            self.logs_dir
        ]
        
        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)
            logger.debug(f"Directory ready: {directory}")
        
        logger.info(f"Project directories setup complete at: {self.project_dir}")
    
    def save_scripts(self, scripts_data: List[Dict]) -> str:
        """
        Save scripts data to JSON file
        
        Args:
            scripts_data: List of script segments
            
        Returns:
            Path to saved file
        """
        output_file = self.scripts_dir / "scripts.json"
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(scripts_data, f, ensure_ascii=False, indent=2)
        
        logger.info(f"Scripts saved to: {output_file}")
        return str(output_file)
    
    def save_images_metadata(self, images_data: List[Dict]) -> str:
        """
        Save images metadata to JSON file
        
        Args:
            images_data: List of image metadata
            
        Returns:
            Path to saved file
        """
        output_file = self.scripts_dir / "images_metadata.json"
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(images_data, f, ensure_ascii=False, indent=2)
        
        logger.info(f"Images metadata saved to: {output_file}")
        return str(output_file)
    
    def get_project_info(self) -> Dict:
        """Get project information"""
        return {
            "project_name": self.project_name,
            "project_dir": str(self.project_dir),
            "output_dir": str(self.output_dir),
            "images_dir": str(self.images_dir),
            "scripts_dir": str(self.scripts_dir),
            "logs_dir": str(self.logs_dir)
        }

