package com.aml.workbench.feature.alerts.evidence

import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.Add
import androidx.compose.material.icons.filled.ArrowBack
import androidx.compose.material.icons.filled.Info
import androidx.compose.material.icons.filled.Link
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.hilt.navigation.compose.hiltViewModel
import com.aml.workbench.core.designsystem.AmlDimens
import com.aml.workbench.core.designsystem.components.AmlRuleOutcomeRow
import com.aml.workbench.core.domain.model.RuleEvaluationSnapshot

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun EvidenceScreen(
    onNavigateBack: () -> Unit,
    onNavigateToCase: (String) -> Unit,
    viewModel: EvidenceViewModel = hiltViewModel()
) {
    val uiState by viewModel.uiState.collectAsState()
    val snackbarHostState = remember { SnackbarHostState() }
    
    LaunchedEffect(uiState.caseCreated, uiState.caseCreationError) {
        uiState.caseCreated?.let { caseRef ->
            val result = snackbarHostState.showSnackbar(
                message = "Case $caseRef created",
                actionLabel = "View case",
                duration = SnackbarDuration.Short
            )
            if (result == SnackbarResult.ActionPerformed) {
                onNavigateToCase(caseRef)
            }
            viewModel.onEvent(EvidenceEvent.ClearCaseCreationFeedback)
        }
        uiState.caseCreationError?.let { message ->
            snackbarHostState.showSnackbar(
                message = message,
                duration = SnackbarDuration.Short
            )
            viewModel.onEvent(EvidenceEvent.ClearCaseCreationFeedback)
        }
    }
    
    Scaffold(
        snackbarHost = { SnackbarHost(snackbarHostState) },
        topBar = {
            TopAppBar(
                title = { 
                    Text(
                        text = uiState.evidence?.alertRef ?: "Loading...",
                        style = MaterialTheme.typography.titleLarge
                    ) 
                },
                navigationIcon = {
                    IconButton(onClick = onNavigateBack) {
                        Icon(Icons.Default.ArrowBack, contentDescription = "Navigate up")
                    }
                },
                actions = {
                    TextButton(onClick = { /* TODO: Audit history */ }) {
                        Text("Audit")
                    }
                }
            )
        },
        bottomBar = {
            Surface(
                modifier = Modifier.fillMaxWidth(),
                color = MaterialTheme.colorScheme.surfaceContainerHigh,
                tonalElevation = 3.dp
            ) {
                Column(
                    modifier = Modifier
                        .fillMaxWidth()
                        .padding(AmlDimens.SpacingLg)
                        .windowInsetsPadding(WindowInsets.navigationBars),
                    verticalArrangement = Arrangement.spacedBy(AmlDimens.SpacingMd)
                ) {
                    Row(
                        modifier = Modifier.fillMaxWidth(),
                        horizontalArrangement = Arrangement.spacedBy(8.dp)
                    ) {
                        Button(
                            onClick = { viewModel.onEvent(EvidenceEvent.CreateCase) },
                            modifier = Modifier
                                .weight(1f)
                                .height(AmlDimens.ButtonHeight),
                            enabled = !uiState.isCreatingCase
                        ) {
                            if (uiState.isCreatingCase) {
                                CircularProgressIndicator(
                                    modifier = Modifier.size(18.dp),
                                    strokeWidth = 2.dp,
                                    color = MaterialTheme.colorScheme.onPrimary
                                )
                                Spacer(modifier = Modifier.width(8.dp))
                            } else {
                                Icon(
                                    Icons.Default.Add,
                                    contentDescription = null,
                                    modifier = Modifier.size(18.dp)
                                )
                                Spacer(modifier = Modifier.width(8.dp))
                            }
                            Text("Create case")
                        }
                        
                        OutlinedButton(
                            onClick = { /* TODO: Link to existing case */ },
                            modifier = Modifier
                                .weight(1.3f)
                                .height(AmlDimens.ButtonHeight)
                        ) {
                            Icon(
                                Icons.Default.Link,
                                contentDescription = null,
                                modifier = Modifier.size(18.dp)
                            )
                            Spacer(modifier = Modifier.width(8.dp))
                            Text("Link to existing case")
                        }
                    }
                    
                    Text(
                        text = "Case creation carries the alert, transaction facts and rule snapshot forward.",
                        style = MaterialTheme.typography.bodySmall,
                        color = MaterialTheme.colorScheme.onSurfaceVariant,
                        modifier = Modifier.fillMaxWidth()
                    )
                }
            }
        }
    ) { paddingValues ->
        when {
            uiState.isLoading -> {
                Box(
                    modifier = Modifier
                        .fillMaxSize()
                        .padding(paddingValues),
                    contentAlignment = Alignment.Center
                ) {
                    CircularProgressIndicator()
                }
            }
            
            uiState.error != null -> {
                Box(
                    modifier = Modifier
                        .fillMaxSize()
                        .padding(paddingValues),
                    contentAlignment = Alignment.Center
                ) {
                    Column(
                        horizontalAlignment = Alignment.CenterHorizontally,
                        verticalArrangement = Arrangement.spacedBy(AmlDimens.SpacingLg)
                    ) {
                        Icon(
                            Icons.Default.Info,
                            contentDescription = null,
                            modifier = Modifier.size(48.dp),
                            tint = MaterialTheme.colorScheme.error
                        )
                        Text(
                            text = "Evidence could not be loaded",
                            style = MaterialTheme.typography.titleMedium
                        )
                        Text(
                            text = uiState.error!!,
                            style = MaterialTheme.typography.bodyMedium,
                            color = MaterialTheme.colorScheme.onSurfaceVariant
                        )
                        Button(onClick = { viewModel.onEvent(EvidenceEvent.Retry) }) {
                            Text("Retry")
                        }
                    }
                }
            }
            
            uiState.evidence != null -> {
                EvidenceContent(
                    uiState = uiState,
                    modifier = Modifier.padding(paddingValues)
                )
            }
        }
    }
}

@Composable
private fun EvidenceContent(
    uiState: EvidenceUiState,
    modifier: Modifier = Modifier
) {
    val evidence = uiState.evidence ?: return
    
    LazyColumn(
        modifier = modifier.fillMaxSize(),
        contentPadding = PaddingValues(AmlDimens.SpacingLg),
        verticalArrangement = Arrangement.spacedBy(AmlDimens.SpacingLg)
    ) {
        // Header with status badges
        item {
            Column(verticalArrangement = Arrangement.spacedBy(8.dp)) {
                Text(
                    text = "TRANSFER REVIEW · ALERT EVIDENCE",
                    style = MaterialTheme.typography.labelMedium,
                    color = MaterialTheme.colorScheme.primary
                )
                
                Row(
                    horizontalArrangement = Arrangement.spacedBy(8.dp),
                    modifier = Modifier.fillMaxWidth()
                ) {
                    Surface(
                        color = when (evidence.priority) {
                            "Critical" -> MaterialTheme.colorScheme.errorContainer
                            "High" -> MaterialTheme.colorScheme.error.copy(alpha = 0.1f)
                            else -> MaterialTheme.colorScheme.surfaceVariant
                        },
                        shape = MaterialTheme.shapes.small
                    ) {
                        Text(
                            text = "${evidence.priority} · Score ${evidence.riskScore}",
                            style = MaterialTheme.typography.labelMedium,
                            modifier = Modifier.padding(horizontal = 8.dp, vertical = 4.dp)
                        )
                    }
                    
                    Surface(
                        color = MaterialTheme.colorScheme.primaryContainer,
                        shape = MaterialTheme.shapes.small
                    ) {
                        Text(
                            text = "Status: ${evidence.status}",
                            style = MaterialTheme.typography.labelMedium,
                            modifier = Modifier.padding(horizontal = 8.dp, vertical = 4.dp)
                        )
                    }
                    
                    Surface(
                        color = MaterialTheme.colorScheme.surfaceVariant,
                        shape = MaterialTheme.shapes.small
                    ) {
                        Text(
                            text = "${evidence.transaction.sourceCountryCode} → ${evidence.transaction.destinationCountryCode}",
                            style = MaterialTheme.typography.labelMedium,
                            modifier = Modifier.padding(horizontal = 8.dp, vertical = 4.dp)
                        )
                    }
                }
            }
        }
        
        // Transaction Facts Card
        item {
            ElevatedCard(
                modifier = Modifier.fillMaxWidth()
            ) {
                Column(
                    modifier = Modifier.padding(AmlDimens.SpacingLg),
                    verticalArrangement = Arrangement.spacedBy(AmlDimens.SpacingMd)
                ) {
                    Text(
                        text = "Transaction facts",
                        style = MaterialTheme.typography.titleMedium,
                        fontWeight = FontWeight.SemiBold
                    )
                    
                    Text(
                        text = "${evidence.transaction.currencyCode} ${evidence.transaction.amount}",
                        style = MaterialTheme.typography.titleLarge,
                        fontWeight = FontWeight.Bold
                    )
                    
                    Column(verticalArrangement = Arrangement.spacedBy(10.dp)) {
                        FactRow("Customer", "${evidence.customer.customerName} · ${evidence.customer.customerId}")
                        FactRow("Transaction", evidence.transaction.transactionRef)
                        FactRow("Date and time", evidence.transaction.executedAtUtc)
                        FactRow("Account", "${evidence.account.accountRef} · ${evidence.account.accountType}")
                        FactRow("Corridor", "${evidence.transaction.sourceCountryCode} → ${evidence.transaction.destinationCountryCode}")
                    }
                    
                    HorizontalDivider()
                    
                    Row(
                        horizontalArrangement = Arrangement.spacedBy(6.dp),
                        verticalAlignment = Alignment.CenterVertically
                    ) {
                        Surface(
                            color = MaterialTheme.colorScheme.surfaceVariant,
                            shape = MaterialTheme.shapes.small
                        ) {
                            Text(
                                text = evidence.alertRef,
                                style = MaterialTheme.typography.labelMedium,
                                modifier = Modifier.padding(horizontal = 8.dp, vertical = 4.dp)
                            )
                        }
                        
                        Text("→", color = MaterialTheme.colorScheme.onSurfaceVariant)
                        
                        Surface(
                            color = MaterialTheme.colorScheme.surfaceVariant,
                            shape = MaterialTheme.shapes.small
                        ) {
                            Text(
                                text = evidence.transaction.transactionRef,
                                style = MaterialTheme.typography.labelMedium,
                                modifier = Modifier.padding(horizontal = 8.dp, vertical = 4.dp)
                            )
                        }
                        
                        Text("→", color = MaterialTheme.colorScheme.onSurfaceVariant)
                        
                        Surface(
                            color = MaterialTheme.colorScheme.surfaceVariant,
                            shape = MaterialTheme.shapes.small
                        ) {
                            Text(
                                text = evidence.customer.customerName,
                                style = MaterialTheme.typography.labelMedium,
                                modifier = Modifier.padding(horizontal = 8.dp, vertical = 4.dp)
                            )
                        }
                    }
                }
            }
        }
        
        // Rule Evaluation Snapshot Card
        item {
            OutlinedCard(
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
                            text = "Rule evaluation snapshot",
                            style = MaterialTheme.typography.titleMedium,
                            fontWeight = FontWeight.SemiBold
                        )
                        
                        Surface(
                            color = MaterialTheme.colorScheme.surfaceVariant,
                            shape = MaterialTheme.shapes.small
                        ) {
                            Row(
                                modifier = Modifier.padding(horizontal = 8.dp, vertical = 4.dp),
                                horizontalArrangement = Arrangement.spacedBy(4.dp),
                                verticalAlignment = Alignment.CenterVertically
                            ) {
                                Icon(
                                    Icons.Default.Info,
                                    contentDescription = null,
                                    modifier = Modifier.size(14.dp)
                                )
                                Text(
                                    text = "Read-only",
                                    style = MaterialTheme.typography.labelMedium
                                )
                            }
                        }
                    }
                    
                    Surface(
                        color = MaterialTheme.colorScheme.primaryContainer.copy(alpha = 0.3f),
                        shape = MaterialTheme.shapes.small
                    ) {
                        Row(
                            modifier = Modifier
                                .fillMaxWidth()
                                .padding(12.dp),
                            horizontalArrangement = Arrangement.spacedBy(12.dp)
                        ) {
                            Icon(
                                Icons.Default.Info,
                                contentDescription = null,
                                modifier = Modifier.size(20.dp),
                                tint = MaterialTheme.colorScheme.primary
                            )
                            Text(
                                text = "Historical versions used at evaluation — not the latest rules.",
                                style = MaterialTheme.typography.bodySmall,
                                color = MaterialTheme.colorScheme.onPrimaryContainer
                            )
                        }
                    }
                    
                    // Mock rule snapshots for display (actual data would come from API)
                    Column {
                        AmlRuleOutcomeRow(
                            ruleName = "Large cross-border transfer",
                            ruleVersion = "v3.2",
                            outcome = "MATCH",
                            conditionText = "USD 48,500 > threshold USD 25,000",
                            evaluatedAtUtc = evidence.triggeredAtUtc
                        )
                        
                        HorizontalDivider()
                        
                        AmlRuleOutcomeRow(
                            ruleName = "High-risk customer",
                            ruleVersion = "v2.1",
                            outcome = "MATCH",
                            conditionText = "Customer risk tier High ≥ threshold High",
                            evaluatedAtUtc = evidence.triggeredAtUtc
                        )
                        
                        HorizontalDivider()
                        
                        AmlRuleOutcomeRow(
                            ruleName = "Restricted country check",
                            ruleVersion = "v4.0",
                            outcome = "PASS",
                            conditionText = "${evidence.transaction.sourceCountryCode} and ${evidence.transaction.destinationCountryCode} are not on the restricted list",
                            evaluatedAtUtc = evidence.triggeredAtUtc
                        )
                    }
                    
                    Text(
                        text = "2 rules matched, 1 rule passed. Snapshots are stored at evaluation time and cannot be edited.",
                        style = MaterialTheme.typography.bodySmall,
                        color = MaterialTheme.colorScheme.onSurfaceVariant
                    )
                }
            }
        }
    }
}

@Composable
private fun FactRow(label: String, value: String) {
    Row(
        modifier = Modifier.fillMaxWidth(),
        horizontalArrangement = Arrangement.SpaceBetween
    ) {
        Text(
            text = label,
            style = MaterialTheme.typography.bodySmall,
            color = MaterialTheme.colorScheme.onSurfaceVariant,
            modifier = Modifier.width(112.dp)
        )
        Text(
            text = value,
            style = MaterialTheme.typography.bodyMedium,
            modifier = Modifier.weight(1f)
        )
    }
}
