package com.aml.workbench.core.designsystem

import androidx.compose.ui.unit.dp

/**
 * AML Workbench spacing and dimension tokens based on a 4dp baseline grid.
 * All layouts, component paddings, and margin insets follow these values.
 */
object AmlDimens {
    // Spacing Scale (4dp baseline grid)
    val Spacing2xs = 2.dp  // Micro badge insets, stroke offsets, hairline separators
    val SpacingXs = 4.dp   // Tight inline gaps, icon-to-text gaps in chips, status indicator margins
    val SpacingSm = 8.dp   // Default inner component padding, small item gaps, chip horizontal padding
    val SpacingMd = 12.dp  // Form field vertical padding, compact card internal padding, badge padding
    val SpacingLg = 16.dp  // Standard screen horizontal margin, card content padding, button padding
    val SpacingXl = 20.dp  // Large card insets, modal bottom sheet internal margin
    val Spacing2xl = 24.dp // Major section breaks, card-to-card vertical gaps, dialog content padding
    val Spacing3xl = 32.dp // Header-to-content separation, empty state hero spacing
    val Spacing4xl = 48.dp // Bottom fixed action bar height clearance, sticky footer safe inset

    // Component Dimensions
    val MinTouchTarget = 48.dp      // Minimum touch target size for accessibility (48dp × 48dp)
    val CardCornerRadius = 12.dp    // Standard card corner radius
    val BannerCornerRadius = 16.dp  // Warning banner and callout corner radius
    val SheetCornerRadius = 28.dp   // Modal bottom sheet top corner radius
    val ButtonHeight = 48.dp        // Standard button height (minimum touch target)
    val InputFieldHeight = 56.dp    // Single-line text input field height
    
    // List Item Heights
    val ListItemHeightOneLine = 56.dp    // Single-line list item
    val ListItemHeightTwoLine = 72.dp    // Two-line list item
    val ListItemHeightThreeLine = 88.dp  // Three-line list item
    
    // Navigation & App Bar Dimensions
    val TopAppBarHeight = 64.dp          // Standard top app bar height
    val TopAppBarHeightMedium = 112.dp   // Medium expanded top app bar height
    val BottomNavigationBarHeight = 80.dp // Bottom navigation bar height
    val NavigationRailWidth = 80.dp      // Navigation rail width (for tablets)
    val NavigationDrawerWidth = 320.dp   // Modal navigation drawer width
    
    // Icon Sizes
    val IconSizeSmall = 16.dp    // Small inline icons
    val IconSizeDefault = 24.dp  // Default icon size
    val IconSizeLarge = 32.dp    // Large emphasis icons
    val IconSizeHero = 48.dp     // Empty state hero icons
    
    // Badge & Chip Dimensions
    val BadgePaddingHorizontal = 8.dp  // Badge horizontal padding
    val BadgePaddingVertical = 4.dp    // Badge vertical padding
    val ChipHeight = 32.dp             // Filter chip height
    
    // Divider & Separator
    val DividerThickness = 0.5.dp  // Standard horizontal divider thickness
    val DividerThicknessBold = 1.dp // Bold separator thickness
    
    // Elevation Levels (dp values for tonal surface system)
    val ElevationLevel0 = 0.dp   // Flat Card, Screen Backdrop
    val ElevationLevel1 = 1.dp   // Hero Alert Card, Transaction Fact Card
    val ElevationLevel2 = 3.dp   // Top App Bar scrolled state, Filter Bar
    val ElevationLevel3 = 6.dp   // Dialogs, Modal Bottom Sheets, Dropdown Menu
    val ElevationLevel4 = 8.dp   // Floating Action Button (FAB), Navigation Bar
    val ElevationLevel5 = 12.dp  // Dragged items, Full modal alerts
}
