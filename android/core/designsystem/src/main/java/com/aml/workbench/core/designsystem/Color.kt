package com.aml.workbench.core.designsystem

import androidx.compose.material3.darkColorScheme
import androidx.compose.material3.lightColorScheme
import androidx.compose.ui.graphics.Color

// Primary Branding Palette
val AmlBluePrimary = Color(0xFF005FCC)
val AmlBlueOnPrimary = Color(0xFFFFFFFF)
val AmlBluePrimaryContainer = Color(0xFFE8F1FF)
val AmlBlueOnPrimaryContainer = Color(0xFF001C3D)
val AmlBlueSecondary = Color(0xFF0066CC)

// Dark Theme Variants
val AmlBluePrimaryDark = Color(0xFFA6CAFF)
val AmlBlueOnPrimaryDark = Color(0xFF003063)
val AmlBluePrimaryContainerDark = Color(0xFF00479A)
val AmlBlueOnPrimaryContainerDark = Color(0xFFD4E3FF)

// Neutrals & Surfaces (Light)
val AmlBackgroundLight = Color(0xFFF8F9FA)
val AmlOnBackgroundLight = Color(0xFF1A1C1E)
val AmlSurfaceLight = Color(0xFFFFFFFF)
val AmlOnSurfaceLight = Color(0xFF1C1C1E)
val AmlSurfaceVariantLight = Color(0xFFEFF1F4)
val AmlOnSurfaceVariantLight = Color(0xFF636366)
val AmlOutlineLight = Color(0xFFD1D1D6)
val AmlOutlineVariantLight = Color(0xFFE5E5EA)

// Surface Container Levels (Light)
val AmlSurfaceContainerLowestLight = Color(0xFFFFFFFF)
val AmlSurfaceContainerLowLight = Color(0xFFF4F5F8)
val AmlSurfaceContainerLight = Color(0xFFEDEDF2)
val AmlSurfaceContainerHighLight = Color(0xFFE7E8ED)
val AmlSurfaceContainerHighestLight = Color(0xFFE1E2E7)

// Neutrals & Surfaces (Dark)
val AmlBackgroundDark = Color(0xFF111318)
val AmlOnBackgroundDark = Color(0xFFE2E2E6)
val AmlSurfaceDark = Color(0xFF191C20)
val AmlOnSurfaceDark = Color(0xFFE2E2E6)
val AmlSurfaceVariantDark = Color(0xFF43474E)
val AmlOnSurfaceVariantDark = Color(0xFFC4C7D0)
val AmlOutlineDark = Color(0xFF8E9199)
val AmlOutlineVariantDark = Color(0xFF43474E)

// Surface Container Levels (Dark)
val AmlSurfaceContainerLowestDark = Color(0xFF0E1013)
val AmlSurfaceContainerLowDark = Color(0xFF17191D)
val AmlSurfaceContainerDark = Color(0xFF1B1E22)
val AmlSurfaceContainerHighDark = Color(0xFF26292E)
val AmlSurfaceContainerHighestDark = Color(0xFF31343A)

// Compliance Semantic Status Colors (Light)
val AmlStatusCritical = Color(0xFFBA1A1A)
val AmlStatusCriticalContainer = Color(0xFFFFEBEA)
val AmlOnStatusCriticalContainer = Color(0xFF410002)

val AmlStatusWarning = Color(0xFF8A4B00)
val AmlStatusWarningContainer = Color(0xFFFFF0D6)
val AmlOnStatusWarningContainer = Color(0xFF2C1600)

val AmlStatusSuccess = Color(0xFF1B6D2F)
val AmlStatusSuccessContainer = Color(0xFFE8F8EE)
val AmlOnStatusSuccessContainer = Color(0xFF002206)

val AmlStatusInfo = Color(0xFF0061A4)
val AmlStatusInfoContainer = Color(0xFFD1E4FF)
val AmlOnStatusInfoContainer = Color(0xFF001D36)

// Compliance Semantic Status Colors (Dark)
val AmlStatusCriticalDark = Color(0xFFFFB4AB)
val AmlStatusCriticalContainerDark = Color(0xFF93000A)
val AmlOnStatusCriticalContainerDark = Color(0xFFFFDAD6)

val AmlStatusWarningDark = Color(0xFFFFB77C)
val AmlStatusWarningContainerDark = Color(0xFF663800)
val AmlOnStatusWarningContainerDark = Color(0xFFFFDCC1)

val AmlStatusSuccessDark = Color(0xFF8CD88D)
val AmlStatusSuccessContainerDark = Color(0xFF00531A)
val AmlOnStatusSuccessContainerDark = Color(0xFFA6F4A8)

val AmlStatusInfoDark = Color(0xFF9FCAFF)
val AmlStatusInfoContainerDark = Color(0xFF00497D)
val AmlOnStatusInfoContainerDark = Color(0xFFD1E4FF)

// Inverse Colors
val AmlInverseSurfaceLight = Color(0xFF2E3033)
val AmlInverseOnSurfaceLight = Color(0xFFF1F0F4)
val AmlInversePrimaryLight = Color(0xFFA6CAFF)

val AmlInverseSurfaceDark = Color(0xFFE2E2E6)
val AmlInverseOnSurfaceDark = Color(0xFF191C20)
val AmlInversePrimaryDark = Color(0xFF005FCC)

// Material 3 Light Color Scheme
val AmlLightColorScheme = lightColorScheme(
    primary = AmlBluePrimary,
    onPrimary = AmlBlueOnPrimary,
    primaryContainer = AmlBluePrimaryContainer,
    onPrimaryContainer = AmlBlueOnPrimaryContainer,
    secondary = AmlBlueSecondary,
    onSecondary = Color.White,
    secondaryContainer = Color(0xFFD6E4FF),
    onSecondaryContainer = Color(0xFF001B3E),
    tertiary = Color(0xFF575E71),
    onTertiary = Color.White,
    tertiaryContainer = Color(0xFFDBE2F9),
    onTertiaryContainer = Color(0xFF141B2C),
    background = AmlBackgroundLight,
    onBackground = AmlOnBackgroundLight,
    surface = AmlSurfaceLight,
    onSurface = AmlOnSurfaceLight,
    surfaceVariant = AmlSurfaceVariantLight,
    onSurfaceVariant = AmlOnSurfaceVariantLight,
    surfaceContainerLowest = AmlSurfaceContainerLowestLight,
    surfaceContainerLow = AmlSurfaceContainerLowLight,
    surfaceContainer = AmlSurfaceContainerLight,
    surfaceContainerHigh = AmlSurfaceContainerHighLight,
    surfaceContainerHighest = AmlSurfaceContainerHighestLight,
    outline = AmlOutlineLight,
    outlineVariant = AmlOutlineVariantLight,
    inverseSurface = AmlInverseSurfaceLight,
    inverseOnSurface = AmlInverseOnSurfaceLight,
    inversePrimary = AmlInversePrimaryLight,
    error = AmlStatusCritical,
    errorContainer = AmlStatusCriticalContainer,
    onError = Color.White,
    onErrorContainer = AmlOnStatusCriticalContainer,
    scrim = Color(0xFF000000)
)

// Material 3 Dark Color Scheme
val AmlDarkColorScheme = darkColorScheme(
    primary = AmlBluePrimaryDark,
    onPrimary = AmlBlueOnPrimaryDark,
    primaryContainer = AmlBluePrimaryContainerDark,
    onPrimaryContainer = AmlBlueOnPrimaryContainerDark,
    secondary = Color(0xFF82B1FF),
    onSecondary = Color(0xFF00325B),
    secondaryContainer = Color(0xFF00497E),
    onSecondaryContainer = Color(0xFFD6E4FF),
    tertiary = Color(0xFFBFC6DC),
    onTertiary = Color(0xFF293041),
    tertiaryContainer = Color(0xFF3F4759),
    onTertiaryContainer = Color(0xFFDBE2F9),
    background = AmlBackgroundDark,
    onBackground = AmlOnBackgroundDark,
    surface = AmlSurfaceDark,
    onSurface = AmlOnSurfaceDark,
    surfaceVariant = AmlSurfaceVariantDark,
    onSurfaceVariant = AmlOnSurfaceVariantDark,
    surfaceContainerLowest = AmlSurfaceContainerLowestDark,
    surfaceContainerLow = AmlSurfaceContainerLowDark,
    surfaceContainer = AmlSurfaceContainerDark,
    surfaceContainerHigh = AmlSurfaceContainerHighDark,
    surfaceContainerHighest = AmlSurfaceContainerHighestDark,
    outline = AmlOutlineDark,
    outlineVariant = AmlOutlineVariantDark,
    inverseSurface = AmlInverseSurfaceDark,
    inverseOnSurface = AmlInverseOnSurfaceDark,
    inversePrimary = AmlInversePrimaryDark,
    error = AmlStatusCriticalDark,
    errorContainer = AmlStatusCriticalContainerDark,
    onError = Color(0xFF690005),
    onErrorContainer = AmlOnStatusCriticalContainerDark,
    scrim = Color(0xFF000000)
)
