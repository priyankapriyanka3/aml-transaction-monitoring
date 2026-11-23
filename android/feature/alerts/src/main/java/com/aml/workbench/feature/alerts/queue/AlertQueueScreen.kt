package com.aml.workbench.feature.alerts.queue

import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.LazyRow
import androidx.compose.foundation.lazy.items
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.Check
import androidx.compose.material.icons.filled.Search
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.hilt.navigation.compose.hiltViewModel
import com.aml.workbench.core.designsystem.AmlDimens
import com.aml.workbench.core.designsystem.components.AmlHeroAlertCard
import com.aml.workbench.core.domain.model.Alert

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun AlertQueueScreen(
    onNavigateToEvidence: (String) -> Unit,
    viewModel: AlertQueueViewModel = hiltViewModel()
) {
    val uiState by viewModel.uiState.collectAsState()
    
    // Show snackbar for assignment feedback
    val snackbarHostState = remember { SnackbarHostState() }
    
    LaunchedEffect(uiState.assignmentSuccess, uiState.assignmentError) {
        uiState.assignmentSuccess?.let { message ->
            snackbarHostState.showSnackbar(
                message = message,
                actionLabel = "Open",
                duration = SnackbarDuration.Short
            )
            viewModel.onEvent(AlertQueueEvent.ClearAssignmentFeedback)
        }
        uiState.assignmentError?.let { message ->
            snackbarHostState.showSnackbar(
                message = message,
                duration = SnackbarDuration.Short
            )
            viewModel.onEvent(AlertQueueEvent.ClearAssignmentFeedback)
        }
    }
    
    Scaffold(
        snackbarHost = { SnackbarHost(snackbarHostState) },
        topBar = {
            Column(
                modifier = Modifier.fillMaxWidth()
            ) {
                // Medium Top App Bar with eyebrow and subtitle
                MediumTopAppBar(
                    title = {
                        Column {
                            Text(
                                text = "TRANSFER REVIEW · Riya · Investigator",
                                style = MaterialTheme.typography.labelMedium,
                                color = MaterialTheme.colorScheme.primary
                            )
                            Spacer(modifier = Modifier.height(4.dp))
                            Text(
                                text = "Alerts",
                                style = MaterialTheme.typography.displaySmall,
                                fontWeight = FontWeight.Bold
                            )
                            Spacer(modifier = Modifier.height(4.dp))
                            Text(
                                text = "Review queue / highest priority first",
                                style = MaterialTheme.typography.bodyMedium,
                                color = MaterialTheme.colorScheme.onSurfaceVariant
                            )
                        }
                    }
                )
            }
        }
    ) { paddingValues ->
        Column(
            modifier = Modifier
                .fillMaxSize()
                .padding(paddingValues)
        ) {
            LazyColumn(
                modifier = Modifier
                    .fillMaxSize()
                    .weight(1f),
                contentPadding = PaddingValues(AmlDimens.SpacingLg),
                verticalArrangement = Arrangement.spacedBy(AmlDimens.SpacingLg)
            ) {
                // Search field
                item {
                    OutlinedTextField(
                        value = uiState.searchQuery,
                        onValueChange = { viewModel.onEvent(AlertQueueEvent.Search(it)) },
                        modifier = Modifier.fillMaxWidth(),
                        placeholder = { 
                            Text("Search alert, customer or transaction ID") 
                        },
                        leadingIcon = {
                            Icon(Icons.Default.Search, contentDescription = "Search")
                        },
                        singleLine = true,
                        colors = OutlinedTextFieldDefaults.colors(
                            unfocusedContainerColor = MaterialTheme.colorScheme.surfaceVariant
                        )
                    )
                }
                
                // Filter chips
                item {
                    LazyRow(
                        horizontalArrangement = Arrangement.spacedBy(8.dp),
                        modifier = Modifier.fillMaxWidth()
                    ) {
                        item {
                            FilterChip(
                                selected = uiState.priorityFilter != null,
                                onClick = { 
                                    viewModel.onEvent(
                                        AlertQueueEvent.FilterByPriority(null)
                                    ) 
                                },
                                label = { Text("Priority: All") }
                            )
                        }
                        
                        item {
                            FilterChip(
                                selected = uiState.ownershipFilter == "Unassigned",
                                onClick = { 
                                    viewModel.onEvent(
                                        AlertQueueEvent.FilterByOwnership("Unassigned")
                                    ) 
                                },
                                label = { Text("Owner: Unassigned") },
                                leadingIcon = if (uiState.ownershipFilter == "Unassigned") {
                                    { Icon(Icons.Default.Check, contentDescription = null, modifier = Modifier.size(16.dp)) }
                                } else null
                            )
                        }
                        
                        item {
                            FilterChip(
                                selected = uiState.statusFilter == "New",
                                onClick = { 
                                    viewModel.onEvent(
                                        AlertQueueEvent.FilterByStatus("New")
                                    ) 
                                },
                                label = { Text("Status: New") },
                                leadingIcon = if (uiState.statusFilter == "New") {
                                    { Icon(Icons.Default.Check, contentDescription = null, modifier = Modifier.size(16.dp)) }
                                } else null
                            )
                        }
                    }
                }
                
                // Queue header
                item {
                    Row(
                        modifier = Modifier.fillMaxWidth(),
                        horizontalArrangement = Arrangement.SpaceBetween,
                        verticalAlignment = Alignment.CenterVertically
                    ) {
                        Text(
                            text = "${uiState.total} alerts · highest priority first",
                            style = MaterialTheme.typography.titleSmall,
                            fontWeight = FontWeight.SemiBold
                        )
                        Text(
                            text = "Refreshed now",
                            style = MaterialTheme.typography.bodySmall,
                            color = MaterialTheme.colorScheme.onSurfaceVariant
                        )
                    }
                }
                
                // Loading state
                if (uiState.isLoading && uiState.alerts.isEmpty()) {
                    item {
                        Box(
                            modifier = Modifier
                                .fillMaxWidth()
                                .padding(AmlDimens.SpacingXl),
                            contentAlignment = Alignment.Center
                        ) {
                            CircularProgressIndicator()
                        }
                    }
                }
                
                // Error state
                if (uiState.error != null) {
                    item {
                        Card(
                            modifier = Modifier.fillMaxWidth(),
                            colors = CardDefaults.cardColors(
                                containerColor = MaterialTheme.colorScheme.errorContainer
                            )
                        ) {
                            Column(
                                modifier = Modifier.padding(AmlDimens.SpacingLg),
                                verticalArrangement = Arrangement.spacedBy(AmlDimens.SpacingMd)
                            ) {
                                Text(
                                    text = "Failed to load alerts",
                                    style = MaterialTheme.typography.titleMedium,
                                    color = MaterialTheme.colorScheme.onErrorContainer
                                )
                                Text(
                                    text = uiState.error!!,
                                    style = MaterialTheme.typography.bodyMedium,
                                    color = MaterialTheme.colorScheme.onErrorContainer
                                )
                                Button(
                                    onClick = { viewModel.onEvent(AlertQueueEvent.Refresh) }
                                ) {
                                    Text("Retry")
                                }
                            }
                        }
                    }
                }
                
                // Hero alert (first item)
                if (uiState.alerts.isNotEmpty()) {
                    item {
                        val heroAlert = uiState.alerts.first()
                        AmlHeroAlertCard(
                            alertId = heroAlert.alertRef,
                            priorityLabel = heroAlert.priority,
                            priorityScore = heroAlert.riskScore,
                            transactionId = "TX-${heroAlert.alertId.toString().takeLast(4)}",
                            amountFormatted = "${heroAlert.transactionCurrencyCode} ${heroAlert.transactionAmount}",
                            corridor = "${heroAlert.sourceCountryCode} → ${heroAlert.destinationCountryCode}",
                            customerName = heroAlert.customerName,
                            status = heroAlert.status,
                            onAssignClick = {
                                viewModel.onEvent(AlertQueueEvent.AssignAlert(heroAlert.alertRef))
                            }
                        )
                    }
                    
                    // More in queue header
                    if (uiState.alerts.size > 1) {
                        item {
                            Text(
                                text = "More in queue",
                                style = MaterialTheme.typography.titleSmall,
                                fontWeight = FontWeight.SemiBold
                            )
                        }
                    }
                }
                
                // Secondary alert cards
                items(uiState.alerts.drop(1)) { alert ->
                    AlertQueueCard(
                        alert = alert,
                        onAssignClick = {
                            viewModel.onEvent(AlertQueueEvent.AssignAlert(alert.alertRef))
                        },
                        onCardClick = {
                            onNavigateToEvidence(alert.alertRef)
                        },
                        isAssigning = uiState.assigningAlertId == alert.alertRef
                    )
                }
            }
        }
    }
}

@Composable
private fun AlertQueueCard(
    alert: Alert,
    onAssignClick: () -> Unit,
    onCardClick: () -> Unit,
    isAssigning: Boolean
) {
    OutlinedCard(
        onClick = onCardClick,
        modifier = Modifier.fillMaxWidth()
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
                    text = alert.alertRef,
                    style = MaterialTheme.typography.titleSmall,
                    fontWeight = FontWeight.Bold
                )
                
                Surface(
                    color = when (alert.priority) {
                        "Critical" -> MaterialTheme.colorScheme.errorContainer
                        "High" -> MaterialTheme.colorScheme.error.copy(alpha = 0.1f)
                        else -> MaterialTheme.colorScheme.surfaceVariant
                    },
                    shape = MaterialTheme.shapes.small
                ) {
                    Text(
                        text = "${alert.priority} · Score ${alert.riskScore}",
                        style = MaterialTheme.typography.labelMedium,
                        modifier = Modifier.padding(horizontal = 8.dp, vertical = 4.dp)
                    )
                }
            }
            
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceBetween,
                verticalAlignment = Alignment.CenterVertically
            ) {
                Text(
                    text = "${alert.transactionCurrencyCode} ${alert.transactionAmount}",
                    style = MaterialTheme.typography.titleMedium
                )
                Text(
                    text = "${alert.sourceCountryCode} → ${alert.destinationCountryCode}",
                    style = MaterialTheme.typography.labelLarge
                )
            }
            
            Text(
                text = "Customer: ${alert.customerName}",
                style = MaterialTheme.typography.bodyMedium
            )
            
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceBetween,
                verticalAlignment = Alignment.CenterVertically
            ) {
                Text(
                    text = "Status: ${alert.status}",
                    style = MaterialTheme.typography.bodySmall,
                    color = MaterialTheme.colorScheme.onSurfaceVariant
                )
                
                if (alert.ownerUserId == null) {
                    TextButton(onClick = onAssignClick, enabled = !isAssigning) {
                        if (isAssigning) {
                            CircularProgressIndicator(
                                modifier = Modifier.size(16.dp),
                                strokeWidth = 2.dp
                            )
                            Spacer(modifier = Modifier.width(8.dp))
                        }
                        Text("Assign to me")
                    }
                } else {
                    Surface(
                        color = MaterialTheme.colorScheme.primaryContainer,
                        shape = MaterialTheme.shapes.small
                    ) {
                        Text(
                            text = "Owned",
                            style = MaterialTheme.typography.labelMedium,
                            modifier = Modifier.padding(horizontal = 8.dp, vertical = 4.dp)
                        )
                    }
                }
            }
        }
    }
}
