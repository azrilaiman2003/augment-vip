"""
IDE database cleaner module
"""

import os
import sys
import sqlite3
import xml.etree.ElementTree as ET
import shutil
from pathlib import Path
from typing import List, Dict, Any, Optional

from .utils import info, success, error, warning, get_ide_paths, backup_file, get_search_terms, _check_term_match

def clean_vscode_db() -> bool:
    """
    Clean VS Code databases by removing entries containing encoded terms (legacy function)
    
    Returns:
        True if successful, False otherwise
    """
    return clean_ide_db("vscode", None)

def clean_ide_db(ide_key: str, base_path: Path) -> bool:
    """
    Clean IDE databases by removing entries containing encoded terms
    
    Args:
        ide_key: IDE identifier key
        base_path: Base directory path for the IDE
    
    Returns:
        True if successful, False otherwise
    """
    info(f"Starting database cleanup process for {ide_key}")
    
    paths = get_ide_paths(ide_key, base_path)
    
    if ide_key in ["vscode", "vscode-insiders", "cursor", "codium"]:
        return clean_vscode_based_ide(ide_key, paths)
    
    elif ide_key in ["intellij", "pycharm", "webstorm", "phpstorm"]:
        return clean_jetbrains_ide(ide_key, paths)
    
    else:
        error(f"Unsupported IDE for cleaning: {ide_key}")
        return False

def clean_vscode_based_ide(ide_key: str, paths: Dict[str, Path]) -> bool:
    """
    Clean VS Code-based IDE databases (SQLite)
    
    Args:
        ide_key: IDE identifier key
        paths: Dictionary of IDE paths
        
    Returns:
        True if successful, False otherwise
    """
    state_db = paths.get("state_db")
    
    if not state_db or not state_db.exists():
        warning(f"IDE database not found at: {state_db}")
        return False
    
    info(f"Found IDE database at: {state_db}")
    
    backup_path = backup_file(state_db)
    
    search_terms = get_search_terms()
    
    try:
        conn = sqlite3.connect(str(state_db))
        cursor = conn.cursor()
        
        conditions = []
        for term in search_terms:
            conditions.append(f"key LIKE '%{term}%'")
        
        where_clause = " OR ".join(conditions)
        
        count_query = f"SELECT COUNT(*) FROM ItemTable WHERE {where_clause}"
        cursor.execute(count_query)
        count_before = cursor.fetchone()[0]
        
        if count_before == 0:
            info("No target entries found in the database")
            conn.close()
            return True
        
        delete_query = f"DELETE FROM ItemTable WHERE {where_clause}"
        cursor.execute(delete_query)
        conn.commit()
        
        cursor.execute(count_query)
        count_after = cursor.fetchone()[0]
        
        conn.close()
        
        success(f"Removed {count_before - count_after} target entries from the database")
        return True
        
    except sqlite3.Error as e:
        error(f"SQLite error: {e}")
        
        if backup_path.exists():
            info("Restoring from backup...")
            try:
                shutil.copy2(backup_path, state_db)
                success("Restored from backup")
            except Exception as restore_error:
                error(f"Failed to restore from backup: {restore_error}")
        
        return False
    except Exception as e:
        error(f"Unexpected error: {e}")
        return False

def clean_jetbrains_ide(ide_key: str, paths: Dict[str, Path]) -> bool:
    """
    Clean JetBrains IDE configuration files (XML)
    
    Args:
        ide_key: IDE identifier key
        paths: Dictionary of IDE paths
        
    Returns:
        True if successful, False otherwise
    """
    config_xml = paths.get("config_xml")
    ide_general_xml = paths.get("ide_general_xml")
    
    success_count = 0
    total_files = 0
    
    if config_xml and config_xml.exists():
        total_files += 1
        info(f"Found config file at: {config_xml}")
        if clean_jetbrains_xml_file(config_xml):
            success_count += 1
    
    if ide_general_xml and ide_general_xml.exists():
        total_files += 1
        info(f"Found IDE general config at: {ide_general_xml}")
        if clean_jetbrains_xml_file(ide_general_xml):
            success_count += 1
    
    if total_files == 0:
        warning("No JetBrains configuration files found")
        return False
    
    if success_count == total_files:
        success(f"Successfully cleaned all {total_files} configuration file(s)")
        return True
    elif success_count > 0:
        warning(f"Cleaned {success_count} out of {total_files} configuration file(s)")
        return True
    else:
        error("Failed to clean any configuration files")
        return False

def clean_jetbrains_xml_file(xml_file: Path) -> bool:
    """
    Clean a single JetBrains XML configuration file
    
    Args:
        xml_file: Path to the XML file to clean
        
    Returns:
        True if successful, False otherwise
    """
    try:
        backup_path = backup_file(xml_file)
        
        tree = ET.parse(xml_file)
        root = tree.getroot()
        
        search_terms = get_search_terms()
        
        removed_count = 0
        
        elements_to_remove = []
        
        for elem in root.iter():
            if elem.text and _check_term_match(elem.text, search_terms):
                elements_to_remove.append(elem)
                continue
            
            for attr_name, attr_value in elem.attrib.items():
                if attr_value and _check_term_match(attr_value, search_terms):
                    elements_to_remove.append(elem)
                    break
        
        elements_to_remove = list(set(elements_to_remove))
        
        for elem in elements_to_remove:
            parent = root.find(f".//*[{elem.tag}]/..")
            if parent is not None:
                parent.remove(elem)
                removed_count += 1
        
        for recent_projects in root.iter("RecentProjectMetaInfo"):
            for project in recent_projects.findall(".//option[@name='projectPath']"):
                if project.get("value") and _check_term_match(project.get("value"), search_terms):
                    recent_projects.remove(project.getparent())
                    removed_count += 1
        
        for recent_files in root.iter("RecentFiles"):
            for file_elem in recent_files.findall(".//option"):
                if file_elem.get("value") and _check_term_match(file_elem.get("value"), search_terms):
                    recent_files.remove(file_elem)
                    removed_count += 1
        
        if removed_count == 0:
            info("No target entries found in the configuration file")
            return True
        
        tree.write(xml_file, encoding='utf-8', xml_declaration=True)
        
        success(f"Removed {removed_count} target entries from {xml_file.name}")
        return True
        
    except ET.ParseError as e:
        error(f"XML parsing error in {xml_file}: {e}")
        
        if backup_path.exists():
            info("Restoring from backup...")
            try:
                shutil.copy2(backup_path, xml_file)
                success("Restored from backup")
            except Exception as restore_error:
                error(f"Failed to restore from backup: {restore_error}")
        
        return False
    except Exception as e:
        error(f"Unexpected error while cleaning {xml_file}: {e}")
        
        if backup_path and backup_path.exists():
            info("Restoring from backup...")
            try:
                shutil.copy2(backup_path, xml_file)
                success("Restored from backup")
            except Exception as restore_error:
                error(f"Failed to restore from backup: {restore_error}")
        
        return False
