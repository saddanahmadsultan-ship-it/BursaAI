"""
=========================================================
BursaAI Service Manifest
Version : 6.0 Sprint 6G.1
=========================================================
"""

SERVICE_GROUPS = {
    "framework": [
        "event_bus",
        "cache_manager",
        "plugin_manager",
        "configuration",
    ],
    "analysis": [
        "engine_registry",
        "pipeline",
        "framework_logger",
        "engine_profiler",
        "event_audit",
    ],
    "portfolio": [
        "portfolio_allocator_adapter",
    ],
    "paper_trading": [
        "paper_account",
        "paper_execution_engine",
        "paper_portfolio",
    ],
    "notifications": [
        "notification_hub",
    ],
    "journal": [
        "trade_journal",
        "event_journal_bridge",
    ],
    "analytics": [
        "performance_engine",
    ],
    "walkforward": [
        "historical_data_loader",
        "historical_dataframe_validator",
        "historical_dataset_cache",
        "historical_dataset_builder",
        "dataset_splitter",
        "dataset_split_validator",
        "historical_engine",
        "training_registry",
        "training_window_runner",
        "validation_registry",
        "validation_window_runner",
        "walkforward_analyzer",
        "optimization_parameter_space",
        "optimization_parameter_generator",
        "optimization_registry",
        "optimization_engine",
        "optimization_workflow",
        "walkforward_final_report_builder",
        "walkforward_final_report_exporter",
        "walkforward_pipeline_registry",
        "walkforward_pipeline",
    ],
}
