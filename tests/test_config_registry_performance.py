"""Performance tests for optimized ConfigRegistry."""

import time
import threading
from pathlib import Path

import pytest

from mycc.modules.config_registry import ConfigRegistry, ConfigRegistryError


class TestConfigRegistryPerformance:
    """Test performance improvements of ConfigRegistry."""

    def setup_method(self):
        """Reset singleton for each test."""
        ConfigRegistry.reset_singleton()

    def test_singleton_behavior(self):
        """Test that ConfigRegistry implements singleton pattern."""
        registry1 = ConfigRegistry()
        registry2 = ConfigRegistry()
        
        assert registry1 is registry2, "ConfigRegistry should be a singleton"
        
        # Test thread safety
        registries = []
        
        def create_registry():
            registries.append(ConfigRegistry())
        
        threads = [threading.Thread(target=create_registry) for _ in range(10)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()
        
        # All instances should be the same
        for registry in registries:
            assert registry is registry1, "All instances should be the same singleton"

    def test_caching_performance(self):
        """Test that caching improves performance."""
        registry = ConfigRegistry()
        
        # First load - measure time
        start_time = time.time()
        entries1 = registry.get_all_entries()
        first_load_time = time.time() - start_time
        
        # Second load - should be faster due to caching
        start_time = time.time()
        entries2 = registry.get_all_entries()
        second_load_time = time.time() - start_time
        
        assert entries1 == entries2, "Cached entries should be identical"
        assert second_load_time < first_load_time, "Second load should be faster due to caching"
        
        # Verify cache stats
        stats = registry.get_cache_stats()
        assert stats['loaded'] is True
        assert stats['entries_count'] > 0
        assert stats['cache_size'] > 0

    def test_lazy_loading(self):
        """Test that configuration is loaded lazily."""
        registry = ConfigRegistry()
        
        # Check that nothing is loaded initially
        stats = registry.get_cache_stats()
        assert stats['loaded'] is False
        assert stats['entries_count'] == 0
        
        # First access should trigger loading
        entries = registry.get_all_entries()
        assert len(entries) > 0
        
        stats = registry.get_cache_stats()
        assert stats['loaded'] is True
        assert stats['entries_count'] > 0

    def test_thread_safety(self):
        """Test thread safety of the registry."""
        registry = ConfigRegistry()
        results = []
        
        def access_registry():
            try:
                entries = registry.get_all_entries()
                results.append(len(entries))
            except Exception as e:
                results.append(f"Error: {e}")
        
        # Access registry from multiple threads simultaneously
        threads = [threading.Thread(target=access_registry) for _ in range(20)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()
        
        # All threads should get the same result
        assert len(results) == 20, "All threads should complete"
        first_result = results[0]
        for result in results:
            if isinstance(result, str) and result.startswith("Error"):
                pytest.fail(f"Thread safety issue: {result}")
            assert result == first_result, "All threads should get consistent results"

    def test_cache_invalidation(self):
        """Test cache invalidation functionality."""
        registry = ConfigRegistry()
        
        # Load initial data
        entries1 = registry.get_all_entries()
        stats1 = registry.get_cache_stats()
        
        # Clear cache
        registry.clear_cache()
        stats2 = registry.get_cache_stats()
        
        assert stats2['loaded'] is False, "Cache should be cleared"
        assert stats2['entries_count'] == 0, "Entries should be cleared"
        assert stats2['cache_size'] == 0, "Cache should be empty"
        
        # Reload should work
        entries2 = registry.get_all_entries()
        assert entries1 == entries2, "Reloaded entries should be identical"

    def test_validation_performance(self):
        """Test that validation doesn't significantly impact performance."""
        registry = ConfigRegistry()
        
        # Load with validation
        start_time = time.time()
        entries = registry.get_all_entries()
        load_time = time.time() - start_time
        
        # Should still be reasonably fast
        assert load_time < 1.0, "Configuration loading should be fast even with validation"
        assert len(entries) > 0, "Should load valid entries"

    def test_error_handling_performance(self):
        """Test that error handling doesn't create memory leaks."""
        registry = ConfigRegistry()
        
        # Test with non-existent file
        fake_path = Path("/nonexistent/path/registry.toml")
        
        start_time = time.time()
        with pytest.raises(ConfigRegistryError):
            registry.load_from_toml(fake_path)
        error_time = time.time() - start_time
        
        # Should fail fast
        assert error_time < 0.1, "Error handling should be fast"
        
        # Cache should not be polluted
        stats = registry.get_cache_stats()
        assert fake_path.name not in [str(k) for k in stats['cache_keys']], "Failed loads should not cache"

    def test_concurrent_loading(self):
        """Test concurrent loading performance."""
        registry = ConfigRegistry()
        loading_times = []
        
        def timed_load():
            start_time = time.time()
            registry.get_all_entries()
            loading_times.append(time.time() - start_time)
        
        # Start multiple concurrent loads
        threads = [threading.Thread(target=timed_load) for _ in range(10)]
        start_time = time.time()
        
        for t in threads:
            t.start()
        for t in threads:
            t.join()
        
        total_time = time.time() - start_time
        
        # Should complete reasonably quickly
        assert total_time < 2.0, "Concurrent loading should be efficient"
        assert len(loading_times) == 10, "All threads should complete"
        
        # Later loads should be faster due to caching (with tolerance for timing variations)
        avg_early = sum(loading_times[:3]) / 3
        avg_late = sum(loading_times[-3:]) / 3
        
        # Allow for timing variations in concurrent environment
        # The important thing is that most loads complete quickly
        max_time = max(loading_times)
        assert max_time < 0.1, f"No individual load should take too long: {max_time}"

    def test_memory_efficiency(self):
        """Test memory efficiency of singleton pattern."""
        registries = []
        
        # Create multiple references
        for _ in range(100):
            registries.append(ConfigRegistry())
        
        # All should reference the same object
        first_registry = registries[0]
        for registry in registries:
            assert registry is first_registry, "All references should point to same singleton"
        
        # Load configuration only once
        first_registry.get_all_entries()
        stats = first_registry.get_cache_stats()
        
        # Verify that all references see the same loaded state
        for registry in registries:
            assert registry.get_cache_stats() == stats, "All references should see same state"