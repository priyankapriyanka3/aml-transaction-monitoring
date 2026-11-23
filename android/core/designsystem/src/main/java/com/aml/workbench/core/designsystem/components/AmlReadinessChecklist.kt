package com.aml.workbench.core.designsystem.components

import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.size
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.rounded.CheckCircle
import androidx.compose.material3.Icon
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.unit.dp
import com.aml.workbench.core.designsystem.AmlDimens
import com.aml.workbench.core.designsystem.AmlStatusSuccess

/**
 * Readiness Verification Checklist
 * 
 * Step 5 review preparation showing clear green checkmarks for all compliance prerequisites
 * before handoff to independent officer. Used in Screen 5 (Review Readiness).
 * 
 * Design specifications from design.md section 4.4:
 * - Checkmark Icon: Icons.Rounded.CheckCircle (20dp, statusSuccess)
 * - Items: 4 compliance prerequisites with verification status
 * - Layout: Row with icon + Column(title + description)
 * 
 * Example items:
 * 1. [✓] Linked evidence — 2 alerts with transactions and historical rule results
 * 2. [✓] Investigation notes — Latest narrative saved by Riya
 * 3. [✓] Responses reviewed — IR-012 · supporting documents received 09 Nov
 * 4. [✓] No open or overdue requests — 0 unresolved requests
 * 
 * @param items List of checklist items to display
 * @param modifier Optional modifier for the checklist container
 */
@Composable
fun AmlReadinessChecklist(
    items: List<ChecklistItem>,
    modifier: Modifier = Modifier
) {
    Column(
        modifier = modifier.fillMaxWidth(),
        verticalArrangement = Arrangement.spacedBy(AmlDimens.SpacingMd)
    ) {
        items.forEach { item ->
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.spacedBy(AmlDimens.SpacingMd),
                verticalAlignment = Alignment.Top
            ) {
                Icon(
                    imageVector = Icons.Rounded.CheckCircle,
                    contentDescription = if (item.isComplete) "Complete" else "Incomplete",
                    tint = if (item.isComplete) AmlStatusSuccess else MaterialTheme.colorScheme.outline,
                    modifier = Modifier.size(20.dp)
                )
                
                Column(
                    modifier = Modifier.weight(1f),
                    verticalArrangement = Arrangement.spacedBy(AmlDimens.Spacing2xs)
                ) {
                    Text(
                        text = item.title,
                        style = MaterialTheme.typography.bodyMedium.copy(
                            fontWeight = androidx.compose.ui.text.font.FontWeight.SemiBold
                        ),
                        color = MaterialTheme.colorScheme.onSurface
                    )
                    
                    if (item.description.isNotEmpty()) {
                        Text(
                            text = item.description,
                            style = MaterialTheme.typography.bodySmall,
                            color = MaterialTheme.colorScheme.onSurfaceVariant
                        )
                    }
                }
            }
        }
    }
}

/**
 * Data class representing a single checklist item
 * 
 * @param title The main checklist item title (e.g., "Linked evidence")
 * @param description Optional explanatory description (e.g., "2 alerts with transactions and historical rule results")
 * @param isComplete Whether the item is complete (shows green checkmark when true)
 */
data class ChecklistItem(
    val title: String,
    val description: String = "",
    val isComplete: Boolean = true
)
