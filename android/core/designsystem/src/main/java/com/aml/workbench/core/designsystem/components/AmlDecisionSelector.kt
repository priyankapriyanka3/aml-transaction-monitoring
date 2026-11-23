package com.aml.workbench.core.designsystem.components

import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.selection.selectable
import androidx.compose.foundation.selection.selectableGroup
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.RadioButton
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.semantics.Role
import com.aml.workbench.core.designsystem.AmlDimens

/**
 * Officer Decision Radio Group & Rationale Box
 * 
 * Step 6 final decision interface for Officer Morgan with radio button selection and
 * mandatory rationale text field. Used in Screen 6 (Officer Review).
 * 
 * Design specifications from design.md section 4.6:
 * - Options: Approve, Reject, Escalate, Close as false positive
 * - Component: Column of selectable list rows with RadioButton
 * - Rationale: Mandatory OutlinedTextField (implemented separately as a parameter)
 * 
 * @param options List of decision options to display
 * @param selectedOption Currently selected decision option
 * @param onOptionSelected Callback invoked when an option is selected
 * @param modifier Optional modifier for the selector container
 */
@Composable
fun AmlDecisionSelector(
    options: List<DecisionOption>,
    selectedOption: String,
    onOptionSelected: (String) -> Unit,
    modifier: Modifier = Modifier
) {
    Column(
        modifier = modifier
            .fillMaxWidth()
            .selectableGroup(),
        verticalArrangement = Arrangement.spacedBy(AmlDimens.SpacingXs)
    ) {
        options.forEach { option ->
            Row(
                modifier = Modifier
                    .fillMaxWidth()
                    .selectable(
                        selected = (selectedOption == option.value),
                        onClick = { onOptionSelected(option.value) },
                        role = Role.RadioButton
                    )
                    .padding(vertical = AmlDimens.SpacingSm),
                horizontalArrangement = Arrangement.spacedBy(AmlDimens.SpacingMd),
                verticalAlignment = Alignment.CenterVertically
            ) {
                RadioButton(
                    selected = (selectedOption == option.value),
                    onClick = null // null recommended for performance - click handled by Row
                )
                
                Column(
                    modifier = Modifier.weight(1f),
                    verticalArrangement = Arrangement.spacedBy(AmlDimens.Spacing2xs)
                ) {
                    Text(
                        text = option.label,
                        style = MaterialTheme.typography.bodyLarge,
                        color = MaterialTheme.colorScheme.onSurface
                    )
                    
                    if (option.description.isNotEmpty()) {
                        Text(
                            text = option.description,
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
 * Data class representing a single decision option
 * 
 * @param value The internal value identifier (e.g., "approve", "reject", "escalate", "close_false_positive")
 * @param label The display label for the option (e.g., "Approve", "Close as false positive")
 * @param description Optional explanatory description for the decision outcome
 */
data class DecisionOption(
    val value: String,
    val label: String,
    val description: String = ""
)
