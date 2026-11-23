package com.aml.workbench.core.designsystem.components

import androidx.compose.foundation.BorderStroke
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.padding
import androidx.compose.material3.CardDefaults
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.OutlinedCard
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.ui.Modifier
import androidx.compose.ui.unit.dp
import com.aml.workbench.core.designsystem.AmlDimens
import com.aml.workbench.core.designsystem.AmlShapes

/**
 * Four-Eyes Segregation of Duties Card
 * 
 * Prevents self-approval by enforcing that the reviewing officer is distinct from the case creator.
 * Used in Screen 5 (Review Readiness) to display four-eyes compliance mandate.
 * 
 * Design specifications from design.md section 4.5:
 * - Accent Container: surfaceContainerLow with primary border stroke (1dp)
 * - Callout: "Independent review required"
 * - Mandate: "Case creator [name] cannot decide this case. The reviewing officer must be a different person."
 * - Officer Selector: Exposed Dropdown (implemented separately as a parameter)
 * 
 * @param caseCreatorName The name of the investigator who created the case (e.g., "Riya")
 * @param mandate Explanatory text about the four-eyes requirement
 * @param officerSelector Composable for selecting the reviewing officer (e.g., Dropdown)
 * @param modifier Optional modifier for the card container
 */
@Composable
fun AmlFourEyesCard(
    caseCreatorName: String,
    mandate: String = "Case creator $caseCreatorName cannot decide this case. The reviewing officer must be a different person.",
    officerSelector: @Composable () -> Unit,
    modifier: Modifier = Modifier
) {
    OutlinedCard(
        modifier = modifier.fillMaxWidth(),
        shape = AmlShapes.medium,
        border = BorderStroke(1.dp, MaterialTheme.colorScheme.primary),
        colors = CardDefaults.outlinedCardColors(
            containerColor = MaterialTheme.colorScheme.surfaceContainerLow
        )
    ) {
        Column(
            modifier = Modifier
                .fillMaxWidth()
                .padding(AmlDimens.SpacingLg),
            verticalArrangement = Arrangement.spacedBy(AmlDimens.SpacingMd)
        ) {
            Text(
                text = "Independent review required",
                style = MaterialTheme.typography.titleMedium,
                color = MaterialTheme.colorScheme.primary
            )
            
            Text(
                text = mandate,
                style = MaterialTheme.typography.bodyMedium,
                color = MaterialTheme.colorScheme.onSurface
            )
            
            // Officer selector composable (e.g., ExposedDropdownMenuBox)
            officerSelector()
        }
    }
}
