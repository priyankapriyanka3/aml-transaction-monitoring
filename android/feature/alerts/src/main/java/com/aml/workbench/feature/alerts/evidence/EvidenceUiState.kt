package com.aml.workbench.feature.alerts.evidence

import com.aml.workbench.core.domain.model.AlertEvidence
import com.aml.workbench.core.domain.model.RuleEvaluationSnapshot

data class EvidenceUiState(
    val evidence: AlertEvidence? = null,
    val ruleSnapshots: List<RuleEvaluationSnapshot> = emptyList(),
    val isLoading: Boolean = false,
    val error: String? = null,
    val isCreatingCase: Boolean = false,
    val caseCreated: String? = null,
    val caseCreationError: String? = null
)

sealed interface EvidenceEvent {
    data object CreateCase : EvidenceEvent
    data object Retry : EvidenceEvent
    data object ClearCaseCreationFeedback : EvidenceEvent
}
