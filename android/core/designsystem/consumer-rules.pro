# Consumer ProGuard rules for designsystem module
# These rules are applied to modules that depend on this module

# Keep public API of design system
-keep public class com.aml.workbench.core.designsystem.** { public *; }
