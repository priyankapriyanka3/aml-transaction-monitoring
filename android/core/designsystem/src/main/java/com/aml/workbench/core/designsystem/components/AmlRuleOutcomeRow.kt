package com.aml.workbench.core.designsystem.components

import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.padding
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Surface
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.unit.dp
import com.aml.workbench.core.designsystem.AmlDimens
import com.aml.workbench.core.designsystem.AmlOnStatusCriticalContainer
import com.aml.workbench.core.designsystem.AmlOnStatusSuccessContainer
import com.aml.workbench.core.designsystem.AmlShapes
import com.aml.workbench.core.designsystem.AmlStatusCriticalContainer
import com.aml.workbench.core.designsystem.AmlStatusSuccessContainer

/**
 * Rule Evaluation Outcome Row (Immutable History)
 * 
 * Displays exact conditions explaining why a transaction was flagged, preserving historical
 * rule versioning snapshots. Used in Screen 2 (Alert Evidence) to show immutable rule evaluations.
 * 
 * Design specifications from design.md section 4.2:
 * - Rule Name & Version: bodyMedium, SemiBold (e.g., "Large cross-border transfer · v3.2")
 * - Outcome Badge: MATCH (Red pill: statusCriticalContainer) or PASS (Green pill: statusSuccessContainer)
 * - Condition Text: bodySmall, onSurfaceVariant (e.g., "USD 48,500 > threshold USD 25,000")
 * 
 * @param ruleName The name of the rule (e.g., "Large cross-border transfer")
 * @param ruleVersion The historical version of the rule at evaluation time (e.g., "v3.2")
 * @param outcome The evaluation outcome: "MATCH" (flagged) or "PASS" (not flagged)
 * @param conditionText Explanatory text describing why the rule matched or passed
 * @param modifier Optional modifier for the row container
 */
@Composable
fun AmlRuleOutcomeRow(
    ruleName: String,
    ruleVersion: String,
    outcome: String,
    conditionText: String,
    modifier: Modifier = Modifier
) {
    val isMatch = outcome.uppercase() == "MATCH"
    val badgeColor = if (isMatch) AmlStatusCriticalContainer else AmlStatusSuccessContainer
    val badgeTextColor = if (isMatch) AmlOnStatusCriticalContainer else AmlOnStatusSuccessContainer
    
    Column(
        modifier = modifier.fillMaxWidth(),
        verticalArrangement = Arrangement.spacedBy(AmlDimens.SpacingXs)
    ) {
        Row(
            modifier = Modifier.fillMaxWidth(),
            horizontalArrangement = Arrangement.SpaceBetween,
            verticalAlignment = Alignment.CenterVertically
        ) {
            Text(
                text = "$ruleName · $ruleVersion",
                style = MaterialTheme.typography.bodyMedium.copy(
                    fontWeight = androidx.compose.ui.text.font.FontWeight.SemiBold
                ),
                color = MaterialTheme.colorScheme.onSurface,
                modifier = Modifier.weight(1f)
            )
            
            Surface(
                color = badgeColor,
                shape = AmlShapes.small
            ) {
                Text(
                    text = outcome.uppercase(),
                    style = MaterialTheme.typography.labelMedium,
                    color = badgeTextColor,
                    modifier = Modifier.padding(horizontal = 8.dp, vertical = 4.dp)
                )
            }
        }
        
        Text(
            text = conditionText,
            style = MaterialTheme.typography.bodySmall,
            color = MaterialTheme.colorScheme.onSurfaceVariant
        )
    }
}
