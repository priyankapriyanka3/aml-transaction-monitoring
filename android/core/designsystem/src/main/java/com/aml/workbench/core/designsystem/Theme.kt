package com.aml.workbench.core.designsystem

import android.app.Activity
import android.os.Build
import androidx.compose.foundation.isSystemInDarkTheme
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.dynamicDarkColorScheme
import androidx.compose.material3.dynamicLightColorScheme
import androidx.compose.runtime.Composable
import androidx.compose.runtime.SideEffect
import androidx.compose.ui.graphics.toArgb
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.platform.LocalView
import androidx.core.view.WindowCompat

/**
 * AML Workbench Material 3 Theme
 * 
 * Provides a complete Material Design 3 theme implementation with:
 * - Light and Dark color schemes based on AML blue primary branding (#005FCC)
 * - Compliance semantic status colors (critical, warning, success, info)
 * - Complete Material 3 typography scale with Inter font family
 * - Shape scale with appropriate corner radii for all component types
 * - Edge-to-edge system bar handling for Android 14+ predictive back
 * 
 * @param darkTheme Whether to use dark theme (defaults to system setting)
 * @param dynamicColor Whether to use Material You dynamic colors (disabled by default to preserve brand identity)
 * @param content The composable content to wrap with this theme
 */
@Composable
fun AmlWorkbenchTheme(
    darkTheme: Boolean = isSystemInDarkTheme(),
    dynamicColor: Boolean = false, // Disabled by default to preserve AML enterprise brand identity
    content: @Composable () -> Unit
) {
    val colorScheme = when {
        dynamicColor && Build.VERSION.SDK_INT >= Build.VERSION_CODES.S -> {
            val context = LocalContext.current
            if (darkTheme) dynamicDarkColorScheme(context) else dynamicLightColorScheme(context)
        }
        darkTheme -> AmlDarkColorScheme
        else -> AmlLightColorScheme
    }

    val view = LocalView.current
    if (!view.isInEditMode) {
        SideEffect {
            val window = (view.context as Activity).window
            // Set system bar colors for edge-to-edge experience
            window.statusBarColor = colorScheme.surface.toArgb()
            window.navigationBarColor = colorScheme.surface.toArgb()
            
            // Configure system bar appearance (light or dark icons)
            val windowInsetsController = WindowCompat.getInsetsController(window, view)
            windowInsetsController.isAppearanceLightStatusBars = !darkTheme
            windowInsetsController.isAppearanceLightNavigationBars = !darkTheme
        }
    }

    MaterialTheme(
        colorScheme = colorScheme,
        typography = AmlTypography,
        shapes = AmlShapes,
        content = content
    )
}
