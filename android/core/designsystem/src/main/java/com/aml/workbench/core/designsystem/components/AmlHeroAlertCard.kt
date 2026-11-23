package com.aml.workbench.core.designsystem.components

import androidx.compose.foundation.BorderStroke
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.material3.Button
import androidx.compose.material3.ButtonDefaults
import androidx.compose.material3.CardDefaults
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.OutlinedCard
import androidx.compose.material3.Surface
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.semantics.semantics
import androidx.compose.ui.unit.dp
import com.aml.workbench.core.designsystem.AmlDimens
import com.aml.workbench.core.designsystem.AmlShapes

/**
 * Hero Alert Queue Card
 * 
 * Displays high-priority alert requiring immediate triage with prominent visual emphasis.
 * Used in Screen 1 (Alert Queue) as the top hero card with 1.5dp primary container border.
 * 
 * Design specifications from design.md section 4.1:
 * - Card: OutlinedCard with 1.5dp stroke in primaryContainer color
 * - Top Row: Alert ID (titleSmall, Bold) + Priority Badge pill (statusCriticalContainer)
 * - Main Metric: Amount (titleLarge, 22sp, Bold) + Corridor Badge
 * - Sub-details: Customer, Transaction ID, Status
 * - Action CTA: Embedded primary Button with explanatory caption
 * 
 * @param alertId Alert identifier (e.g., "AL-1042")
 * @param priorityLabel Priority level label (e.g., "Critical")
 * @param priorityScore Numeric risk score (e.g., 92)
 * @param transactionId Transaction reference (e.g., "TX-8821")
 * @param amountFormatted Formatted transaction amount (e.g., "USD 48,500")
 * @param corridor Transaction corridor/route (e.g., "GB → AE")
 * @param customerName Customer or entity name (e.g., "Northstar Trading")
 * @param status Alert status (e.g., "New")
 * @param onAssignClick Callback invoked when "Assign to me" button is clicked
 * @param modifier Optional modifier for the card container
 */
@Composable
fun AmlHeroAlertCard(
    alertId: String,
    priorityLabel: String,
    priorityScore: Int,
    transactionId: String,
    amountFormatted: String,
    corridor: String,
    customerName: String,
    status: String,
    onAssignClick: () -> Unit,
    modifier: Modifier = Modifier
) {
    OutlinedCard(
        modifier = modifier
            .fillMaxWidth()
            .semantics(mergeDescendants = true) {},
        shape = AmlShapes.medium,
        border = BorderStroke(1.5.dp, MaterialTheme.colorScheme.primaryContainer),
        colors = CardDefaults.outlinedCardColors(containerColor = MaterialTheme.colorScheme.surface)
    ) {
        Column(
            modifier = Modifier.padding(AmlDimens.SpacingLg),
            verticalArrangement = Arrangement.spacedBy(AmlDimens.SpacingMd)
        ) {
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceBetween,
                verticalAlignment = Alignment.CenterVertically
            ) {
                Text(
                    text = alertId,
                    style = MaterialTheme.typography.titleMedium,
                    color = MaterialTheme.colorScheme.onSurface
                )
                Surface(
                    color = MaterialTheme.colorScheme.errorContainer,
                    shape = AmlShapes.small
                ) {
                    Text(
                        text = "$priorityLabel · Score $priorityScore",
                        style = MaterialTheme.typography.labelMedium,
                        color = MaterialTheme.colorScheme.onErrorContainer,
                        modifier = Modifier.padding(horizontal = 8.dp, vertical = 4.dp)
                    )
                }
            }

            Text(
                text = "Transaction $transactionId",
                style = MaterialTheme.typography.bodyMedium,
                color = MaterialTheme.colorScheme.onSurfaceVariant
            )

            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceBetween,
                verticalAlignment = Alignment.CenterVertically
            ) {
                Text(
                    text = amountFormatted,
                    style = MaterialTheme.typography.titleLarge,
                    color = MaterialTheme.colorScheme.onSurface
                )
                Text(
                    text = corridor,
                    style = MaterialTheme.typography.labelLarge,
                    color = MaterialTheme.colorScheme.onSurface
                )
            }

            Text(
                text = "Customer: $customerName",
                style = MaterialTheme.typography.bodyMedium,
                color = MaterialTheme.colorScheme.onSurface
            )

            Text(
                text = "Status: $status",
                style = MaterialTheme.typography.bodySmall,
                color = MaterialTheme.colorScheme.onSurfaceVariant
            )

            Button(
                onClick = onAssignClick,
                modifier = Modifier
                    .fillMaxWidth()
                    .height(AmlDimens.ButtonHeight),
                shape = AmlShapes.medium,
                colors = ButtonDefaults.buttonColors(containerColor = MaterialTheme.colorScheme.primary)
            ) {
                Text(
                    text = "Assign to me",
                    style = MaterialTheme.typography.labelLarge
                )
            }

            Text(
                text = "Assignment moves this alert to Under review.",
                style = MaterialTheme.typography.bodySmall,
                color = MaterialTheme.colorScheme.onSurfaceVariant
            )
        }
    }
}
