package com.aml.workbench.core.designsystem.components

import androidx.compose.foundation.background
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.size
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.rounded.Warning
import androidx.compose.material3.Icon
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.semantics.LiveRegionMode
import androidx.compose.ui.semantics.liveRegion
import androidx.compose.ui.semantics.semantics
import androidx.compose.ui.unit.dp
import com.aml.workbench.core.designsystem.AmlDimens
import com.aml.workbench.core.designsystem.AmlShapes
import com.aml.workbench.core.designsystem.AmlStatusWarning
import com.aml.workbench.core.designsystem.AmlStatusWarningContainer

/**
 * Decision Blocker Warning Banner
 * 
 * Visually and programmatically enforces regulatory blocking when open Information Requests exist.
 * Used in Screen 4 (Resolve Gaps) and Screen 6 (Officer Review) to prevent decisions while
 * evidence gaps remain unresolved.
 * 
 * Design specifications from design.md section 4.3:
 * - Container Fill: statusWarningContainer (#FFF0D6 Light / #663800 Dark)
 * - Shape: RoundedCornerShape(16.dp)
 * - Icon: Warning Triangle (24×24 dp, statusWarning color)
 * - Live region semantics for TalkBack announcement
 * 
 * @param title Banner title text (e.g., "1 open request — decision blocked")
 * @param message Explanatory body text describing the blocker reason
 * @param modifier Optional modifier for the banner container
 */
@Composable
fun AmlDecisionBlockerBanner(
    title: String = "1 open request — decision blocked",
    message: String = "Approval, rejection and closure remain blocked while any request is open or overdue.",
    modifier: Modifier = Modifier
) {
    Row(
        modifier = modifier
            .fillMaxWidth()
            .background(color = AmlStatusWarningContainer, shape = AmlShapes.large)
            .padding(AmlDimens.SpacingLg)
            .semantics { liveRegion = LiveRegionMode.Polite },
        verticalAlignment = Alignment.Top,
        horizontalArrangement = Arrangement.spacedBy(AmlDimens.SpacingMd)
    ) {
        Icon(
            imageVector = Icons.Rounded.Warning,
            contentDescription = "Warning",
            tint = AmlStatusWarning,
            modifier = Modifier.size(24.dp)
        )
        Column(verticalArrangement = Arrangement.spacedBy(AmlDimens.SpacingXs)) {
            Text(
                text = title,
                style = MaterialTheme.typography.titleSmall,
                color = MaterialTheme.colorScheme.onSurface
            )
            Text(
                text = message,
                style = MaterialTheme.typography.bodySmall,
                color = MaterialTheme.colorScheme.onSurfaceVariant
            )
        }
    }
}
