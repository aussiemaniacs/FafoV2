#!/usr/bin/env python3
"""
FafoV2 Kodi Addon Comprehensive Test Suite
Tests the Kodi addon structure, Python code, and compatibility
"""

import os
import sys
import ast
import json
import xml.etree.ElementTree as ET
import re
import subprocess
from pathlib import Path
import importlib.util

class KodiAddonTester:
    def __init__(self, addon_path="/app/plugin.video.fafov2"):
        self.addon_path = Path(addon_path)
        self.tests_run = 0
        self.tests_passed = 0
        self.errors = []
        self.warnings = []
        
    def log_test(self, name, success, details="", warning=False):
        """Log test results"""
        self.tests_run += 1
        if success:
            self.tests_passed += 1
            print(f"✅ {name} - PASSED")
            if details:
                print(f"   Details: {details}")
        else:
            if warning:
                self.warnings.append(f"{name}: {details}")
                print(f"⚠️  {name} - WARNING: {details}")
            else:
                self.errors.append(f"{name}: {details}")
                print(f"❌ {name} - FAILED: {details}")

    def test_addon_structure(self):
        """Test basic addon file structure"""
        print("\n📁 Testing Addon Structure...")
        
        required_files = [
            "addon.xml",
            "default.py",
            "resources/settings.xml",
            "resources/lib/__init__.py",
            "resources/lib/main.py",
            "README.md"
        ]
        
        missing_files = []
        for file_path in required_files:
            full_path = self.addon_path / file_path
            if not full_path.exists():
                missing_files.append(file_path)
        
        if missing_files:
            self.log_test("Required Files", False, f"Missing files: {missing_files}")
        else:
            self.log_test("Required Files", True, "All required files present")
        
        # Check optional but recommended files
        optional_files = [
            "fanart.jpg",
            "icon.png",
            "resources/language/resource.language.en_gb/strings.po"
        ]
        
        missing_optional = []
        for file_path in optional_files:
            full_path = self.addon_path / file_path
            if not full_path.exists():
                missing_optional.append(file_path)
        
        if missing_optional:
            self.log_test("Optional Files", True, f"Missing optional files: {missing_optional}", warning=True)
        else:
            self.log_test("Optional Files", True, "All optional files present")

    def test_addon_xml(self):
        """Test addon.xml format and content"""
        print("\n📄 Testing addon.xml...")
        
        addon_xml_path = self.addon_path / "addon.xml"
        if not addon_xml_path.exists():
            self.log_test("addon.xml Exists", False, "addon.xml not found")
            return
        
        try:
            tree = ET.parse(addon_xml_path)
            root = tree.getroot()
            
            # Check root element
            if root.tag != "addon":
                self.log_test("addon.xml Root Element", False, f"Root element is '{root.tag}', expected 'addon'")
                return
            
            # Check required attributes
            required_attrs = ["id", "name", "version", "provider-name"]
            missing_attrs = []
            for attr in required_attrs:
                if attr not in root.attrib:
                    missing_attrs.append(attr)
            
            if missing_attrs:
                self.log_test("addon.xml Attributes", False, f"Missing attributes: {missing_attrs}")
            else:
                addon_id = root.attrib["id"]
                version = root.attrib["version"]
                self.log_test("addon.xml Attributes", True, f"ID: {addon_id}, Version: {version}")
            
            # Check addon ID format
            addon_id = root.attrib.get("id", "")
            if re.match(r"^plugin\.video\.[a-z0-9]+$", addon_id):
                self.log_test("Addon ID Format", True, f"Valid format: {addon_id}")
            else:
                self.log_test("Addon ID Format", False, f"Invalid format: {addon_id}")
            
            # Check version format
            version = root.attrib.get("version", "")
            if re.match(r"^\d+\.\d+\.\d+$", version):
                self.log_test("Version Format", True, f"Valid format: {version}")
            else:
                self.log_test("Version Format", False, f"Invalid format: {version}")
            
            # Check requires section
            requires = root.find("requires")
            if requires is not None:
                imports = requires.findall("import")
                if imports:
                    import_list = [imp.attrib.get("addon", "unknown") for imp in imports]
                    self.log_test("Dependencies", True, f"Found {len(imports)} dependencies: {import_list}")
                else:
                    self.log_test("Dependencies", False, "No import elements found in requires")
            else:
                self.log_test("Dependencies", False, "No requires section found")
            
            # Check extension points
            extensions = root.findall("extension")
            plugin_source = None
            metadata = None
            
            for ext in extensions:
                point = ext.attrib.get("point", "")
                if point == "xbmc.python.pluginsource":
                    plugin_source = ext
                elif point == "xbmc.addon.metadata":
                    metadata = ext
            
            if plugin_source is not None:
                library = plugin_source.attrib.get("library", "")
                provides = plugin_source.find("provides")
                if library == "default.py" and provides is not None and provides.text == "video":
                    self.log_test("Plugin Extension", True, "Valid plugin source extension")
                else:
                    self.log_test("Plugin Extension", False, f"Invalid plugin extension: library={library}")
            else:
                self.log_test("Plugin Extension", False, "No plugin source extension found")
            
            if metadata is not None:
                summary = metadata.find("summary[@lang='en_GB']")
                description = metadata.find("description[@lang='en_GB']")
                if summary is not None and description is not None:
                    self.log_test("Metadata", True, "Summary and description present")
                else:
                    self.log_test("Metadata", False, "Missing summary or description")
            else:
                self.log_test("Metadata", False, "No metadata extension found")
                
        except ET.ParseError as e:
            self.log_test("addon.xml Parse", False, f"XML parsing error: {e}")
        except Exception as e:
            self.log_test("addon.xml Parse", False, f"Unexpected error: {e}")

    def test_settings_xml(self):
        """Test settings.xml format"""
        print("\n⚙️ Testing settings.xml...")
        
        settings_path = self.addon_path / "resources" / "settings.xml"
        if not settings_path.exists():
            self.log_test("settings.xml Exists", False, "settings.xml not found")
            return
        
        try:
            tree = ET.parse(settings_path)
            root = tree.getroot()
            
            if root.tag != "settings":
                self.log_test("settings.xml Root", False, f"Root element is '{root.tag}', expected 'settings'")
                return
            
            categories = root.findall("category")
            if categories:
                category_ids = [cat.attrib.get("id", "unknown") for cat in categories]
                self.log_test("Settings Categories", True, f"Found {len(categories)} categories: {category_ids}")
                
                # Check settings within categories
                total_settings = 0
                for category in categories:
                    settings = category.findall("setting")
                    total_settings += len(settings)
                
                self.log_test("Settings Count", True, f"Total settings: {total_settings}")
            else:
                self.log_test("Settings Categories", False, "No categories found")
                
        except ET.ParseError as e:
            self.log_test("settings.xml Parse", False, f"XML parsing error: {e}")
        except Exception as e:
            self.log_test("settings.xml Parse", False, f"Unexpected error: {e}")

    def test_python_syntax(self):
        """Test Python file syntax"""
        print("\n🐍 Testing Python Syntax...")
        
        python_files = []
        
        # Find all Python files
        for root, dirs, files in os.walk(self.addon_path):
            for file in files:
                if file.endswith('.py'):
                    python_files.append(Path(root) / file)
        
        if not python_files:
            self.log_test("Python Files Found", False, "No Python files found")
            return
        
        syntax_errors = []
        for py_file in python_files:
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    source = f.read()
                
                # Parse the AST to check syntax
                ast.parse(source, filename=str(py_file))
                
            except SyntaxError as e:
                syntax_errors.append(f"{py_file.name}: {e}")
            except UnicodeDecodeError as e:
                syntax_errors.append(f"{py_file.name}: Encoding error - {e}")
            except Exception as e:
                syntax_errors.append(f"{py_file.name}: {e}")
        
        if syntax_errors:
            self.log_test("Python Syntax", False, f"Syntax errors found: {syntax_errors}")
        else:
            self.log_test("Python Syntax", True, f"All {len(python_files)} Python files have valid syntax")

    def test_imports_and_dependencies(self):
        """Test Python imports and dependencies"""
        print("\n📦 Testing Imports and Dependencies...")
        
        python_files = []
        for root, dirs, files in os.walk(self.addon_path):
            for file in files:
                if file.endswith('.py'):
                    python_files.append(Path(root) / file)
        
        import_errors = []
        kodi_imports = set()
        external_imports = set()
        
        for py_file in python_files:
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    source = f.read()
                
                tree = ast.parse(source, filename=str(py_file))
                
                for node in ast.walk(tree):
                    if isinstance(node, ast.Import):
                        for alias in node.names:
                            module_name = alias.name
                            if module_name.startswith('xbmc'):
                                kodi_imports.add(module_name)
                            elif module_name not in ['os', 'sys', 'json', 'logging', 're', 'time', 'datetime', 'uuid', 'urllib', 'pathlib']:
                                external_imports.add(module_name)
                    
                    elif isinstance(node, ast.ImportFrom):
                        if node.module:
                            if node.module.startswith('xbmc'):
                                kodi_imports.add(node.module)
                            elif node.module not in ['os', 'sys', 'json', 'logging', 're', 'time', 'datetime', 'uuid', 'urllib', 'pathlib']:
                                external_imports.add(node.module)
                
            except Exception as e:
                import_errors.append(f"{py_file.name}: {e}")
        
        if import_errors:
            self.log_test("Import Analysis", False, f"Errors analyzing imports: {import_errors}")
        else:
            self.log_test("Import Analysis", True, "Successfully analyzed all imports")
        
        # Check Kodi imports
        expected_kodi_imports = {'xbmc', 'xbmcaddon', 'xbmcgui', 'xbmcplugin', 'xbmcvfs'}
        found_kodi_imports = kodi_imports.intersection(expected_kodi_imports)
        
        if found_kodi_imports:
            self.log_test("Kodi Imports", True, f"Found Kodi imports: {sorted(found_kodi_imports)}")
        else:
            self.log_test("Kodi Imports", False, "No Kodi imports found")
        
        # Check external dependencies
        if external_imports:
            self.log_test("External Dependencies", True, f"External imports: {sorted(external_imports)}", warning=True)
        else:
            self.log_test("External Dependencies", True, "No external dependencies")

    def test_class_structure(self):
        """Test class structure and method definitions"""
        print("\n🏗️ Testing Class Structure...")
        
        main_py = self.addon_path / "resources" / "lib" / "main.py"
        if not main_py.exists():
            self.log_test("Main Module", False, "main.py not found")
            return
        
        try:
            with open(main_py, 'r', encoding='utf-8') as f:
                source = f.read()
            
            tree = ast.parse(source, filename=str(main_py))
            
            classes = []
            functions = []
            
            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    classes.append(node.name)
                    # Check methods in class
                    methods = [n.name for n in node.body if isinstance(n, ast.FunctionDef)]
                    if methods:
                        print(f"   Class {node.name} methods: {methods}")
                elif isinstance(node, ast.FunctionDef) and not any(isinstance(parent, ast.ClassDef) for parent in ast.walk(tree)):
                    functions.append(node.name)
            
            if classes:
                self.log_test("Class Definitions", True, f"Found classes: {classes}")
            else:
                self.log_test("Class Definitions", False, "No classes found in main.py")
            
            if functions:
                self.log_test("Function Definitions", True, f"Found functions: {functions}")
            else:
                self.log_test("Function Definitions", True, "No standalone functions (expected for class-based addon)")
                
        except Exception as e:
            self.log_test("Class Structure Analysis", False, f"Error analyzing structure: {e}")

    def test_entry_point(self):
        """Test default.py entry point"""
        print("\n🚪 Testing Entry Point...")
        
        default_py = self.addon_path / "default.py"
        if not default_py.exists():
            self.log_test("Entry Point Exists", False, "default.py not found")
            return
        
        try:
            with open(default_py, 'r', encoding='utf-8') as f:
                source = f.read()
            
            tree = ast.parse(source, filename=str(default_py))
            
            # Check for main function
            has_main = False
            has_main_call = False
            
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef) and node.name == 'main':
                    has_main = True
                elif isinstance(node, ast.If):
                    # Check for if __name__ == '__main__':
                    if (isinstance(node.test, ast.Compare) and
                        isinstance(node.test.left, ast.Name) and
                        node.test.left.id == '__name__'):
                        has_main_call = True
            
            if has_main:
                self.log_test("Main Function", True, "main() function found")
            else:
                self.log_test("Main Function", False, "No main() function found")
            
            if has_main_call:
                self.log_test("Main Guard", True, "if __name__ == '__main__' guard found")
            else:
                self.log_test("Main Guard", False, "No main guard found")
            
            # Check for sys.argv usage
            if 'sys.argv' in source:
                self.log_test("Plugin Parameters", True, "Uses sys.argv for plugin parameters")
            else:
                self.log_test("Plugin Parameters", False, "No sys.argv usage found")
                
        except Exception as e:
            self.log_test("Entry Point Analysis", False, f"Error analyzing entry point: {e}")

    def test_language_strings(self):
        """Test language strings format"""
        print("\n🌐 Testing Language Strings...")
        
        strings_po = self.addon_path / "resources" / "language" / "resource.language.en_gb" / "strings.po"
        if not strings_po.exists():
            self.log_test("Language File", False, "strings.po not found")
            return
        
        try:
            with open(strings_po, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Count msgid entries
            msgid_count = content.count('msgid "')
            msgstr_count = content.count('msgstr "')
            
            if msgid_count > 0 and msgid_count == msgstr_count:
                self.log_test("Language Strings", True, f"Found {msgid_count} string pairs")
            else:
                self.log_test("Language Strings", False, f"Mismatch: {msgid_count} msgid, {msgstr_count} msgstr")
            
            # Check for numeric IDs (Kodi standard)
            numeric_ids = re.findall(r'msgid "(\d+)"', content)
            if numeric_ids:
                id_ranges = {}
                for id_str in numeric_ids:
                    id_num = int(id_str)
                    range_key = f"{id_num // 100 * 100}-{id_num // 100 * 100 + 99}"
                    id_ranges[range_key] = id_ranges.get(range_key, 0) + 1
                
                self.log_test("String ID Ranges", True, f"ID ranges used: {id_ranges}")
            else:
                self.log_test("String ID Format", False, "No numeric string IDs found")
                
        except Exception as e:
            self.log_test("Language Strings Analysis", False, f"Error analyzing strings: {e}")

    def test_functionality_logic(self):
        """Test functionality and logic patterns"""
        print("\n🔧 Testing Functionality Logic...")
        
        # Test YouTube handler
        youtube_handler = self.addon_path / "resources" / "lib" / "youtube_handler.py"
        if youtube_handler.exists():
            try:
                with open(youtube_handler, 'r', encoding='utf-8') as f:
                    source = f.read()
                
                # Check for yt-dlp integration
                if 'yt_dlp' in source or 'yt-dlp' in source:
                    self.log_test("YouTube Integration", True, "yt-dlp integration found")
                else:
                    self.log_test("YouTube Integration", False, "No yt-dlp integration found")
                
                # Check for URL validation
                if 'youtube.com' in source and 'youtu.be' in source:
                    self.log_test("YouTube URL Handling", True, "YouTube URL patterns found")
                else:
                    self.log_test("YouTube URL Handling", False, "Missing YouTube URL patterns")
                    
            except Exception as e:
                self.log_test("YouTube Handler Analysis", False, f"Error: {e}")
        else:
            self.log_test("YouTube Handler", False, "youtube_handler.py not found")
        
        # Test lists manager
        lists_manager = self.addon_path / "resources" / "lib" / "lists_manager.py"
        if lists_manager.exists():
            try:
                with open(lists_manager, 'r', encoding='utf-8') as f:
                    source = f.read()
                
                # Check for CRUD operations
                crud_methods = ['create', 'get', 'update', 'delete']
                found_crud = [method for method in crud_methods if method in source.lower()]
                
                if len(found_crud) >= 3:
                    self.log_test("Lists CRUD Operations", True, f"Found operations: {found_crud}")
                else:
                    self.log_test("Lists CRUD Operations", False, f"Limited operations: {found_crud}")
                    
            except Exception as e:
                self.log_test("Lists Manager Analysis", False, f"Error: {e}")
        else:
            self.log_test("Lists Manager", False, "lists_manager.py not found")

    def test_error_handling(self):
        """Test error handling patterns"""
        print("\n🛡️ Testing Error Handling...")
        
        python_files = []
        for root, dirs, files in os.walk(self.addon_path):
            for file in files:
                if file.endswith('.py'):
                    python_files.append(Path(root) / file)
        
        try_except_count = 0
        logging_usage = 0
        
        for py_file in python_files:
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    source = f.read()
                
                tree = ast.parse(source, filename=str(py_file))
                
                for node in ast.walk(tree):
                    if isinstance(node, ast.Try):
                        try_except_count += 1
                
                if 'logging' in source or 'logger' in source:
                    logging_usage += 1
                    
            except Exception:
                continue
        
        if try_except_count > 0:
            self.log_test("Exception Handling", True, f"Found {try_except_count} try-except blocks")
        else:
            self.log_test("Exception Handling", False, "No exception handling found")
        
        if logging_usage > 0:
            self.log_test("Logging Usage", True, f"Logging used in {logging_usage} files")
        else:
            self.log_test("Logging Usage", False, "No logging usage found")

    def test_documentation_quality(self):
        """Test documentation completeness"""
        print("\n📚 Testing Documentation...")
        
        readme_path = self.addon_path / "README.md"
        if not readme_path.exists():
            self.log_test("README Exists", False, "README.md not found")
            return
        
        try:
            with open(readme_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Check for key sections
            required_sections = [
                "installation", "features", "usage", "dependencies", 
                "troubleshooting", "support"
            ]
            
            found_sections = []
            for section in required_sections:
                if section.lower() in content.lower():
                    found_sections.append(section)
            
            coverage = len(found_sections) / len(required_sections)
            
            if coverage >= 0.8:
                self.log_test("Documentation Coverage", True, f"Found {len(found_sections)}/{len(required_sections)} sections")
            else:
                self.log_test("Documentation Coverage", False, f"Only {len(found_sections)}/{len(required_sections)} sections found")
            
            # Check length (comprehensive documentation should be substantial)
            word_count = len(content.split())
            if word_count > 1000:
                self.log_test("Documentation Length", True, f"{word_count} words - comprehensive")
            elif word_count > 500:
                self.log_test("Documentation Length", True, f"{word_count} words - adequate", warning=True)
            else:
                self.log_test("Documentation Length", False, f"{word_count} words - too brief")
                
        except Exception as e:
            self.log_test("Documentation Analysis", False, f"Error: {e}")

    def run_all_tests(self):
        """Run all Kodi addon tests"""
        print("🚀 Starting FafoV2 Kodi Addon Comprehensive Tests")
        print(f"📁 Testing addon at: {self.addon_path}")
        print("=" * 70)
        
        # Run all test categories
        self.test_addon_structure()
        self.test_addon_xml()
        self.test_settings_xml()
        self.test_python_syntax()
        self.test_imports_and_dependencies()
        self.test_class_structure()
        self.test_entry_point()
        self.test_language_strings()
        self.test_functionality_logic()
        self.test_error_handling()
        self.test_documentation_quality()
        
        # Print summary
        print("\n" + "=" * 70)
        print(f"📊 Test Results: {self.tests_passed}/{self.tests_run} tests passed")
        
        if self.errors:
            print(f"\n❌ Errors ({len(self.errors)}):")
            for error in self.errors:
                print(f"   • {error}")
        
        if self.warnings:
            print(f"\n⚠️  Warnings ({len(self.warnings)}):")
            for warning in self.warnings:
                print(f"   • {warning}")
        
        # Overall assessment
        success_rate = self.tests_passed / self.tests_run if self.tests_run > 0 else 0
        
        if success_rate >= 0.9:
            print("\n🎉 Excellent! Addon is ready for installation and use.")
            return 0
        elif success_rate >= 0.8:
            print("\n✅ Good! Addon should work with minor issues.")
            return 0
        elif success_rate >= 0.7:
            print("\n⚠️  Fair! Addon may work but has some issues to address.")
            return 1
        else:
            print("\n❌ Poor! Addon has significant issues that need fixing.")
            return 1

def main():
    """Main test runner"""
    tester = KodiAddonTester()
    return tester.run_all_tests()

if __name__ == "__main__":
    sys.exit(main())