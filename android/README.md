# AML Workbench Android Application

Enterprise-grade Android application for Anti-Money Laundering (AML) transaction monitoring and compliance review workflows.

## Architecture

This Android application follows modern Android development best practices:

- **Language**: Kotlin
- **UI Framework**: Jetpack Compose 1.7+ with Material Design 3
- **Minimum SDK**: API 26 (Android 8.0 Oreo)
- **Target SDK**: API 34 (Android 14+)
- **Architecture Pattern**: MVVM + Clean Architecture
- **Modular Structure**: Feature-based modules with core design system

## Module Structure

```
android/
├── core/
│   └── designsystem/          # Material 3 design system implementation
│       ├── Color.kt           # Light & dark color schemes
│       ├── Type.kt            # Typography scale (Inter/Roboto)
│       ├── Shape.kt           # Corner radii definitions
│       ├── Dimens.kt          # Spacing & dimension tokens (4dp grid)
│       ├── Theme.kt           # AmlWorkbenchTheme composable
│       └── components/        # AML-specific reusable components
│           ├── AmlDecisionBlockerBanner.kt
│           ├── AmlHeroAlertCard.kt
│           ├── AmlRuleOutcomeRow.kt
│           ├── AmlReadinessChecklist.kt
│           ├── AmlFourEyesCard.kt
│           └── AmlDecisionSelector.kt
└── [future feature modules]
```

## Design System

The design system implements Material Design 3 with AML-specific branding:

### Color Palette
- **Primary**: #005FCC (AML blue branding)
- **Semantic Status Colors**: Critical (red), Warning (amber), Success (green), Info (blue)
- **Complete Light & Dark Themes**: Full tonal surface elevation system

### Typography Scale
- **Font Family**: Inter (with Roboto fallback)
- **Scale**: Material 3 standard scale from displayLarge (57sp) to labelSmall (11sp)

### Spacing System
- **Baseline Grid**: 4dp
- **Scale**: 2xs (2dp) through 4xl (48dp)
- **Touch Targets**: Minimum 48dp for accessibility

### Shape Scale
- **Extra Small**: 4dp (status indicators, pills)
- **Small**: 8dp (badges)
- **Medium**: 12dp (standard cards)
- **Large**: 16dp (dialogs, banners)
- **Extra Large**: 28dp (bottom sheets)

## Building the Design System Module

### Prerequisites
- JDK 17 or higher
- Android SDK with API 34
- Gradle 8.2+

### Build Commands

```bash
# Navigate to Android directory
cd android

# Make gradlew executable (Unix/Mac)
chmod +x gradlew

# Build the design system module
./gradlew :core:designsystem:assembleDebug

# Run lint checks
./gradlew :core:designsystem:lintDebug

# Run tests
./gradlew :core:designsystem:test

# Clean build
./gradlew clean :core:designsystem:assembleDebug
```

### Windows

```cmd
# Build the design system module
gradlew.bat :core:designsystem:assembleDebug

# Run lint checks
gradlew.bat :core:designsystem:lintDebug
```

## Design System Components

### Core Theme
Use `AmlWorkbenchTheme` to wrap your application:

```kotlin
@Composable
fun MyApp() {
    AmlWorkbenchTheme(
        darkTheme = isSystemInDarkTheme(),
        dynamicColor = false // Preserves AML brand identity
    ) {
        // Your content here
    }
}
```

### Material Tokens Access
```kotlin
// Colors
MaterialTheme.colorScheme.primary
MaterialTheme.colorScheme.surface
MaterialTheme.colorScheme.error

// Typography
MaterialTheme.typography.titleLarge
MaterialTheme.typography.bodyMedium

// Shapes
MaterialTheme.shapes.medium
AmlShapes.large

// Spacing
AmlDimens.SpacingLg
AmlDimens.MinTouchTarget
```

### Compliance Status Colors
```kotlin
// Access semantic status colors directly
AmlStatusCritical          // #BA1A1A
AmlStatusCriticalContainer // #FFEBEA
AmlStatusWarning          // #8A4B00
AmlStatusSuccess          // #1B6D2F
AmlStatusInfo             // #0061A4
```

### Specialized Components

#### Decision Blocker Banner
Enforces regulatory blocking when information requests are open:
```kotlin
AmlDecisionBlockerBanner(
    title = "1 open request — decision blocked",
    message = "Approval, rejection and closure remain blocked while any request is open or overdue."
)
```

#### Hero Alert Card
Prominent alert display for queue prioritization:
```kotlin
AmlHeroAlertCard(
    alertId = "AL-1042",
    priorityLabel = "Critical",
    priorityScore = 92,
    transactionId = "TX-8821",
    amountFormatted = "USD 48,500",
    corridor = "GB → AE",
    customerName = "Northstar Trading",
    status = "New",
    onAssignClick = { /* Handle assignment */ }
)
```

#### Rule Outcome Row
Displays immutable historical rule evaluation results:
```kotlin
AmlRuleOutcomeRow(
    ruleName = "Large cross-border transfer",
    ruleVersion = "v3.2",
    outcome = "MATCH",
    conditionText = "USD 48,500 > threshold USD 25,000"
)
```

#### Readiness Checklist
Four-eyes review preparation verification:
```kotlin
AmlReadinessChecklist(
    items = listOf(
        ChecklistItem("Linked evidence", "2 alerts with transactions", isComplete = true),
        ChecklistItem("Investigation notes", "Latest narrative saved", isComplete = true),
        ChecklistItem("Responses reviewed", "IR-012 received 09 Nov", isComplete = true),
        ChecklistItem("No open requests", "0 unresolved requests", isComplete = true)
    )
)
```

#### Four-Eyes Card
Segregation of duties enforcement:
```kotlin
AmlFourEyesCard(
    caseCreatorName = "Riya",
    officerSelector = {
        // Your officer selection dropdown here
    }
)
```

#### Decision Selector
Final decision radio group for officer review:
```kotlin
AmlDecisionSelector(
    options = listOf(
        DecisionOption("approve", "Approve"),
        DecisionOption("reject", "Reject"),
        DecisionOption("escalate", "Escalate"),
        DecisionOption("close", "Close as false positive")
    ),
    selectedOption = selectedDecision,
    onOptionSelected = { decision -> /* Handle selection */ }
)
```

## Compliance Features

The design system enforces four-eyes segregation of duties and immutable audit requirements:

1. **Four-Eyes Control**: Case creator cannot be the reviewing officer
2. **Immutable Rule Snapshots**: Historical rule versions preserved (v3.2, v2.1, etc.)
3. **Decision Blocking**: UI-level enforcement for open information requests
4. **Audit Attribution**: All state changes tracked with actor and timestamp
5. **Accessibility**: TalkBack support, 48dp touch targets, WCAG 2.1 AA contrast

## Edge-to-Edge Support

The theme configures edge-to-edge display with transparent system bars:

```kotlin
// Apply window insets in your layouts
Modifier.statusBarsPadding()
Modifier.navigationBarsPadding()
Modifier.imePadding() // For keyboard handling
```

## Adaptive Layouts

The design system supports responsive layouts across device sizes:

- **Compact** (<600dp): Phone layout with bottom navigation
- **Medium** (600-840dp): Foldable/small tablet with navigation rail
- **Expanded** (>840dp): Large tablet/DeX with permanent drawer

## Dependencies

Key dependencies managed through Compose BOM:
- `androidx.compose:compose-bom:2024.02.00`
- `androidx.compose.material3:material3`
- `androidx.compose.material:material-icons-extended`
- `androidx.activity:activity-compose:1.8.2`
- `androidx.core:core-ktx:1.12.0`

## Design Specification

This implementation follows the complete design specification in:
- `provided_context/design_system/design.md` (1188 lines)

The specification covers:
- Material 3 color schemes (Section 2.1-2.2)
- Typography scale (Section 2.3)
- Spacing & grid system (Section 2.4)
- Elevation & shapes (Section 2.5-2.6)
- Component specifications (Sections 3-4)
- Screen-by-screen flows (Section 5)
- Accessibility guidelines (Section 7)

## License

Apache License 2.0 - See LICENSE file in repository root.
