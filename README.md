# Flaxon Debug Toolbar

<p align="center">
  <img src="https://raw.githubusercontent.com/aldanedev-create/Flaxon-Backend-Framework/main/assets/flaxon.png" alt="Flaxon Logo" width="200"/>
</p>

<p align="center">
  <a href="https://pypi.org/project/flaxon/"><img src="https://img.shields.io/pypi/v/flaxon.svg" alt="PyPI version"></a>
  <a href="https://github.com/aldanedev-create/Flaxon-Backend-Framework/blob/main/LICENSE"><img src="https://img.shields.io/badge/License-MIT-yellow.svg" alt="License: MIT"></a>
  <a href="https://github.com/astral-sh/ruff"><img src="https://img.shields.io/badge/code%20style-ruff-000000.svg" alt="Code style: ruff"></a>
</p>

**Debug toolbar plugin for the Flaxon framework featuring interactive Three.js 3D visualizations.**

---

## Overview

Flaxon Debug Toolbar is a powerful development tool that provides real-time insights into your Flaxon application. Inspect requests, responses, SQL queries, cache operations, application logs, routing, middleware execution, template rendering, performance timing, and state variables—all accompanied by rich 3D visualizations powered by Three.js.

---

## Features

### Core Features
* 🔍 **Request/Response Inspection** — Inspect headers, payload, status, and precise timing.
* 📊 **SQL Query Logging** — Monitor database query executions and individual execution times.
* 💾 **Cache Operations** — Track cache hits, misses, and store operations.
* 📝 **Logging Panel** — View application log outputs created during request processing.
* 🗺️ **Route Matching** — Identify exactly which route and handler serviced the request.
* 🔗 **Middleware Stack** — Inspect middleware execution order and individual runtimes.
* 📄 **Template Rendering** — Track template compile/rendering durations and context data.
* ⏱️ **Performance Timeline** — Step-by-step breakdown of request lifecycle performance.
* 📦 **Variables Panel** — Inspect request, session, and application state variables.
* ❌ **Error Tracking** — Capture and display uncaught exceptions and errors.

### Three.js 3D Visualizations
* 🎯 **3D Performance Timeline** — Animated 3D bar charts representing execution timing.
* 📊 **3D SQL Query Charts** — Interactive 3D visualization of query performance metrics.
* 🌊 **3D Data Flow Diagrams** — Spatial network representation of request data flow.
* 🎨 **Animated Transitions** — Smooth 3D transformations between panel states.
* 📈 **Interactive 3D Charts** — 3D pie/donut charts for request statistics.
* 🔄 **Animated Status Indicators** — Dynamic 3D indicators for system status.
* 🌐 **3D Network Visualization** — Visual mapping of client/server request flow.

---

## Installation

```bash
pip install flaxon-debug-toolbar
To enable Three.js 3D visualization features, install the optional extra:Bashpip install flaxon-debug-toolbar[three]
Quick StartPythonfrom flaxon import Flaxon
from flaxon_debug_toolbar import DebugToolbarPlugin

app = Flaxon("my-app", debug=True)

# Basic usage
app.plugins.load_plugin(DebugToolbarPlugin())

# With Three.js 3D visualizations enabled
app.plugins.load_plugin(DebugToolbarPlugin(
    three_enabled=True,
    three_theme="dark",
    animate_transitions=True,
    performance_mode="balanced",
))

@app.get("/")
async def home(request):
    return {"message": "Check the debug toolbar!"}
ConfigurationEnvironment VariablesBash# Enable or disable toolbar
DEBUG_TOOLBAR_ENABLED=true

# Three.js settings
DEBUG_TOOLBAR_THREE_ENABLED=true
DEBUG_TOOLBAR_THREE_THEME=dark
DEBUG_TOOLBAR_PERFORMANCE_MODE=balanced

# Placement & Behavior
DEBUG_TOOLBAR_POSITION=bottom
DEBUG_TOOLBAR_SQL_THRESHOLD=100
DEBUG_TOOLBAR_INTERCEPT_REDIRECTS=true
DEBUG_TOOLBAR_AUTO_SHOW=true
Application ConfigPythonapp = Flaxon("my-app", config={
    "DEBUG_TOOLBAR_ENABLED": True,
    "DEBUG_TOOLBAR_THREE_ENABLED": True,
    "DEBUG_TOOLBAR_THREE_THEME": "dark",
    "DEBUG_TOOLBAR_PERFORMANCE_MODE": "balanced",
    "DEBUG_TOOLBAR_POSITION": "bottom",
})

plugin = DebugToolbarPlugin.from_config(app.config)
app.plugins.load_plugin(plugin)
Advanced ConfigurationPythonapp.plugins.load_plugin(DebugToolbarPlugin(
    # Core settings
    enabled=True,
    auto_show=True,
    intercept_redirects=True,
    theme="dark",
    position="bottom",
    
    # Three.js settings
    three_enabled=True,
    three_theme="dark",
    animate_transitions=True,
    performance_mode="balanced",
    
    # Selected panels
    panels=[
        "request",
        "sql",
        "cache",
        "logging",
        "routing",
        "middleware",
        "templates",
        "timeline",
        "variables",
        "errors"
    ],
    
    # Thresholds & Limits
    sql_max_queries=100,
    sql_slow_threshold=100,
    body_truncate=1000,
    show_env=False,
))
Included PanelsPanelDescriptionThree.js FeatureRequestRequest/response details3D globe showing IP geolocationSQLDatabase queries and execution timesInteractive 3D query time chartCacheCache operations and statistics3D hit/miss ratio visualizationLoggingApplication log entries—RoutingMatched route details3D network view of route topologyMiddlewareExecution pipeline order3D vertical stack visualizationTemplatesRendering details & context—TimelineRequest performance breakdownAnimated 3D timeline chartVariablesApplication state & session variables—ErrorsExceptions & backtraces3D severity indicatorPerformance ModesModeDescriptionResource TargetperformanceLow-resource modeDisables particles, uses simple geometry & low-poly meshesbalancedStandard experienceModerate particle usage with medium-density geometryqualityMaximum fidelityHigh-density geometry, particle systems, and shadows enabledThree.js Visualizations Detail3D Performance Timeline: Animated 3D bar chart highlighting processing stages with particle streams indicating flow.3D SQL Query Visualization: Interactive bar charts representing query durations, color-coded by command type (SELECT, INSERT, UPDATE, DELETE).3D Request Flow: Particle animation moving through 3D nodes representing lifecycle processing stages.3D Middleware Stack: Vertical 3D spatial stack representing middleware layer execution and timing.3D Cache Visualization: Donut and pie charts rendered in 3D displaying hit vs. miss proportions.3D Error Severity: Graphical 3D representation highlighting error impact and severity tiers.Extending with Custom PanelsPythonfrom flaxon_debug_toolbar.panels.base import Panel

class CustomPanel(Panel):
    title = "Custom Panel"
    nav_title = "Custom"
    identifier = "custom"
    icon = "⭐"
    order = 50
    has_three_scene = True
    three_scene_class = "CustomScene"

    async def process_request(self, request, data):
        self.custom_data = {"info": "Custom data"}

    async def render(self, context):
        return "<div>Custom Panel Content</div>"

# Register custom panel
app.plugins.get("debug_toolbar").register_panel(CustomPanel())
Screenshots3D Performance TimelineSQL Query VisualizationRequest Flow NetworkTestingBash# Run all tests
pytest

# Run tests with code coverage report
pytest --cov=flaxon_debug_toolbar

# Run tests for specific modules
pytest tests/test_panels.py -v
Security ConsiderationsConcernMitigation StrategyProduction ExposureThe toolbar automatically disables itself outside of explicit debug mode.Data LeakagePasswords, authorization tokens, and secrets are automatically redacted.Performance OverheadThree.js assets and scenes are loaded lazily only when the toolbar is open.Memory FootprintScene objects and webGL resources are disposed on panel transitions.GPU UtilizationAdjustable performance modes allow lowering render load on lighter hardware.Development Roadmapv0.1.0: Initial release with core toolbar and 3D timeline.v0.2.0: SQL query visualization and 3D request flow additions.v0.3.0: 3D cache metrics and route topology visualization.v0.4.0: Performance modes and canvas optimization pass.v0.5.0: Support for custom 3D scenes in user-defined panels.v0.6.0: Real-time 3D telemetry streaming over WebSockets.Related Pluginsflaxon-sentry — Sentry error logging and exception tracking.flaxon-oauth-google — Google OAuth2 authentication provider.flaxon-inertia — Inertia.js adapter for dynamic monolith apps.flaxon-fyr — Integration for Fyr web development tools.ContributingFork the repository.Create your feature or bugfix branch (git checkout -b feature/my-feature).Add tests verifying your changes.Ensure code passes ruff and pytest.Submit a pull request.LicenseDistributed under the MIT License. See LICENSE for details.
