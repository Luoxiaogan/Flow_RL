"""
Dynamic operator loading and management utility
Handles operator registry and group configurations
"""
import csv
import yaml
import os
from typing import Dict, List, Any, Optional
import logging

logger = logging.getLogger(__name__)

class OperatorRegistry:
    """Registry for managing operator definitions and metadata"""
    
    def __init__(self, registry_path: str = None):
        """
        Initialize the operator registry
        
        Args:
            registry_path: Path to the operator registry CSV file
        """
        if registry_path is None:
            # Default path relative to ScoreFlow root
            registry_path = os.path.join(
                os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
                'config', 'operator_registry.csv'
            )
        
        self.operators = {}
        self._load_registry(registry_path)
    
    def _load_registry(self, path: str):
        """Load operator definitions from CSV file"""
        try:
            with open(path, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    self.operators[row['operator_name']] = row
            logger.info(f"Loaded {len(self.operators)} operators from registry")
        except FileNotFoundError:
            logger.error(f"Operator registry file not found: {path}")
            raise
        except Exception as e:
            logger.error(f"Error loading operator registry: {e}")
            raise
    
    def get_operator_info(self, name: str) -> Optional[Dict]:
        """
        Get information for a specific operator
        
        Args:
            name: Name of the operator
            
        Returns:
            Dictionary with operator information or None if not found
        """
        return self.operators.get(name)
    
    def get_operators_by_category(self, category: str) -> List[Dict]:
        """
        Get all operators in a specific category
        
        Args:
            category: Category name (core, code, reasoning, specialized)
            
        Returns:
            List of operator dictionaries
        """
        return [op for op in self.operators.values() 
                if op['category'] == category]
    
    def get_operators_by_module(self, module: str) -> List[Dict]:
        """
        Get all operators from a specific module
        
        Args:
            module: Module path (e.g., 'common.operator', 'MATH.operator')
            
        Returns:
            List of operator dictionaries
        """
        return [op for op in self.operators.values() 
                if op['module_path'] == module]
    
    def get_operators_for_benchmark(self, benchmark: str) -> List[Dict]:
        """
        Get operators that support a specific benchmark
        
        Args:
            benchmark: Benchmark name
            
        Returns:
            List of operator dictionaries
        """
        operators = []
        for op in self.operators.values():
            supported = op['supported_benchmarks']
            if supported == 'all' or benchmark in supported.split('|'):
                operators.append(op)
        return operators
    
    def list_all_operators(self) -> List[str]:
        """Get list of all registered operator names"""
        return list(self.operators.keys())


class OperatorGroupManager:
    """Manager for operator group configurations"""
    
    def __init__(self, groups_path: str = None):
        """
        Initialize the operator group manager
        
        Args:
            groups_path: Path to the operator groups YAML file
        """
        if groups_path is None:
            # Default path relative to ScoreFlow root
            groups_path = os.path.join(
                os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
                'config', 'operator_groups.yaml'
            )
        
        self.groups = {}
        self.registry = OperatorRegistry()
        self._load_groups(groups_path)
    
    def _load_groups(self, path: str):
        """Load operator group configurations from YAML file"""
        try:
            with open(path, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f)
                self.groups = data.get('operator_groups', {})
            logger.info(f"Loaded {len(self.groups)} operator groups")
        except FileNotFoundError:
            logger.error(f"Operator groups file not found: {path}")
            raise
        except Exception as e:
            logger.error(f"Error loading operator groups: {e}")
            raise
    
    def get_group(self, group_name: str) -> Optional[Dict]:
        """
        Get configuration for a specific operator group
        
        Args:
            group_name: Name of the operator group
            
        Returns:
            Dictionary with group configuration or None if not found
        """
        return self.groups.get(group_name)
    
    def list_groups(self) -> List[str]:
        """Get list of all available operator group names"""
        return list(self.groups.keys())
    
    def get_operators_for_group(self, group_name: str) -> List[Dict]:
        """
        Get detailed information for all operators in a group
        
        Args:
            group_name: Name of the operator group
            
        Returns:
            List of operator information dictionaries
        """
        group = self.get_group(group_name)
        if not group:
            return []
        
        operators = []
        for op_name in group.get('operators', []):
            op_info = self.registry.get_operator_info(op_name)
            if op_info:
                operators.append(op_info)
            else:
                logger.warning(f"Operator '{op_name}' not found in registry")
        
        return operators
    
    def get_modules_for_group(self, group_name: str) -> List[str]:
        """
        Get unique module paths used by operators in a group
        
        Args:
            group_name: Name of the operator group
            
        Returns:
            List of unique module paths
        """
        group = self.get_group(group_name)
        if not group:
            return []
        
        # Check if group has explicit module setting
        if group.get('module') and group['module'] != 'mixed':
            return [group['module']]
        
        # Otherwise, collect modules from individual operators
        modules = set()
        for op_info in self.get_operators_for_group(group_name):
            modules.add(op_info['module_path'])
        
        return list(modules)
    
    def validate_group(self, group_name: str) -> tuple:
        """
        Validate that all operators in a group exist in the registry
        
        Args:
            group_name: Name of the operator group
            
        Returns:
            Tuple of (is_valid: bool, missing_operators: List[str])
        """
        group = self.get_group(group_name)
        if not group:
            return False, [f"Group '{group_name}' not found"]
        
        missing = []
        for op_name in group.get('operators', []):
            if not self.registry.get_operator_info(op_name):
                missing.append(op_name)
        
        return len(missing) == 0, missing
    
    def get_group_description(self, group_name: str) -> str:
        """
        Get a formatted description of an operator group
        
        Args:
            group_name: Name of the operator group
            
        Returns:
            Formatted string description
        """
        group = self.get_group(group_name)
        if not group:
            return f"Group '{group_name}' not found"
        
        lines = [
            f"Group: {group_name}",
            f"Name: {group.get('name', 'N/A')}",
            f"Description: {group.get('description', 'N/A')}",
            f"Module: {group.get('module', 'mixed')}",
            f"Operators ({len(group.get('operators', []))}):"
        ]
        
        for op_name in group.get('operators', []):
            op_info = self.registry.get_operator_info(op_name)
            if op_info:
                lines.append(f"  - {op_name}: {op_info['description']}")
            else:
                lines.append(f"  - {op_name}: [NOT FOUND IN REGISTRY]")
        
        return '\n'.join(lines)


# Utility functions for common operations
def get_available_operators_for_benchmark(benchmark: str) -> List[str]:
    """
    Get list of operator names available for a specific benchmark
    
    Args:
        benchmark: Benchmark name
        
    Returns:
        List of operator names
    """
    registry = OperatorRegistry()
    operators = registry.get_operators_for_benchmark(benchmark)
    return [op['operator_name'] for op in operators]


def validate_operator_group_for_benchmark(group_name: str, benchmark: str) -> tuple:
    """
    Check if all operators in a group support a specific benchmark
    
    Args:
        group_name: Name of the operator group
        benchmark: Benchmark name
        
    Returns:
        Tuple of (is_compatible: bool, unsupported_operators: List[str])
    """
    manager = OperatorGroupManager()
    operators = manager.get_operators_for_group(group_name)
    
    unsupported = []
    for op in operators:
        supported = op['supported_benchmarks']
        if supported != 'all' and benchmark not in supported.split('|'):
            unsupported.append(op['operator_name'])
    
    return len(unsupported) == 0, unsupported