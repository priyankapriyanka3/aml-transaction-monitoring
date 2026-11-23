# Consumer ProGuard rules for alerts feature module
# These rules will be included in the consuming application's ProGuard configuration

# Preserve public API surface
-keep public class com.aml.workbench.feature.alerts.** { public *; }
