package com.aml.workbench.feature.alerts.queue

import com.aml.workbench.core.domain.model.Alert

data class AlertQueueUiState(
    val alerts: List<Alert> = emptyList(),
    val total: Int = 0,
    val page: Int = 1,
    val pageSize: Int = 20,
    val isLoading: Boolean = false,
    val error: String? = null,
    val priorityFilter: String? = null,
    val ownershipFilter: String = "Unassigned",
    val statusFilter: String = "New",
    val searchQuery: String = "",
    val assigningAlertId: String? = null,
    val assignmentSuccess: String? = null,
    val assignmentError: String? = null
)

sealed interface AlertQueueEvent {
    data class FilterByPriority(val priority: String?) : AlertQueueEvent
    data class FilterByOwnership(val ownership: String) : AlertQueueEvent
    data class FilterByStatus(val status: String) : AlertQueueEvent
    data class Search(val query: String) : AlertQueueEvent
    data object LoadNextPage : AlertQueueEvent
    data object Refresh : AlertQueueEvent
    data class AssignAlert(val alertRef: String) : AlertQueueEvent
    data object ClearAssignmentFeedback : AlertQueueEvent
}
