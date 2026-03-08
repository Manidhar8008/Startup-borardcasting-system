"""
Core plugin ecosystem to allow 3rd-party developers to extend JAN AI capabilities.
"""
import importlib
import os
import pkgutil
import logging

logger = logging.getLogger("plugin_manager")

class PluginManager:
    def __init__(self, plugin_dir="plugins"):
        self.plugin_dir = plugin_dir
        self.plugins = {}
        self.load_plugins()

    def load_plugins(self):
        """Scans the plugins directory and registers active plugins."""
        if not os.path.exists(self.plugin_dir):
            os.makedirs(self.plugin_dir)
            return

        # Simple mock plugin loading
        for _, module_name, is_pkg in pkgutil.iter_modules([self.plugin_dir]):
            try:
                mod = importlib.import_module(f"{self.plugin_dir}.{module_name}")
                if hasattr(mod, "PLUGIN_NAME") and hasattr(mod, "run"):
                    self.plugins[mod.PLUGIN_NAME] = {
                        "name": mod.PLUGIN_NAME,
                        "description": getattr(mod, "PLUGIN_DESCRIPTION", ""),
                        "module": mod,
                        "version": getattr(mod, "VERSION", "1.0")
                    }
            except Exception as e:
                logger.error(f"Failed to load plugin {module_name}: {e}")

    def list_plugins(self):
        """Returns a list of loaded plugins."""
        return [{"name": p["name"], "description": p["description"], "version": p["version"]} for p in self.plugins.values()]

    def execute_plugin(self, plugin_name: str, **kwargs):
        """Executes a specific plugin's run method."""
        if plugin_name not in self.plugins:
            return {"error": f"Plugin {plugin_name} not found"}
            
        try:
            return self.plugins[plugin_name]["module"].run(**kwargs)
        except Exception as e:
            return {"error": f"Plugin {plugin_name} execution failed: {e}"}
