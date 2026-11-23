package com.aml.workbench.core.designsystem

import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material3.Shapes
import androidx.compose.ui.unit.dp

// Material 3 Shape Scale for AML Workbench
val AmlShapes = Shapes(
    extraSmall = RoundedCornerShape(4.dp),  // Status indicator dots, miniature tag pills
    small = RoundedCornerShape(8.dp),       // Badges (MATCH/PASS), Date Picker inner fields
    medium = RoundedCornerShape(12.dp),     // Standard Cards, Alert items, Reason text box
    large = RoundedCornerShape(16.dp),      // Decision Blocker Banner, Modal Dialogs, Large Cards
    extraLarge = RoundedCornerShape(28.dp)  // Modal Bottom Sheet top corners, Full Search Bar
)

// Full pill shape for Buttons, Filter Chips, and Floating Action Buttons
val PillShape = RoundedCornerShape(percent = 50)
