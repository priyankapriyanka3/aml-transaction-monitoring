package com.aml.workbench.feature.alerts.queue

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.aml.workbench.core.data.repository.AlertRepository
import dagger.hilt.android.lifecycle.HiltViewModel
import kotlinx.coroutines.FlowPreview
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.flow.debounce
import kotlinx.coroutines.flow.distinctUntilChanged
import kotlinx.coroutines.flow.launchIn
import kotlinx.coroutines.flow.onEach
import kotlinx.coroutines.flow.update
import kotlinx.coroutines.launch
import java.util.UUID
import javax.inject.Inject

@OptIn(FlowPreview::class)
@HiltViewModel
class AlertQueueViewModel @Inject constructor(
    private val alertRepository: AlertRepository
) : ViewModel() {
    
    private val _uiState = MutableStateFlow(AlertQueueUiState())
    val uiState: StateFlow<AlertQueueUiState> = _uiState.asStateFlow()
    
    private val searchQueryFlow = MutableStateFlow("")
    
    init {
        // Debounce search input by 300ms
        searchQueryFlow
            .debounce(300)
            .distinctUntilChanged()
            .onEach { query ->
                _uiState.update { it.copy(searchQuery = query) }
                loadAlerts()
            }
            .launchIn(viewModelScope)
        
        // Load initial data
        loadAlerts()
    }
    
    fun onEvent(event: AlertQueueEvent) {
        when (event) {
            is AlertQueueEvent.FilterByPriority -> {
                _uiState.update { it.copy(priorityFilter = event.priority, page = 1) }
                loadAlerts()
            }
            is AlertQueueEvent.FilterByOwnership -> {
                _uiState.update { it.copy(ownershipFilter = event.ownership, page = 1) }
                loadAlerts()
            }
            is AlertQueueEvent.FilterByStatus -> {
                _uiState.update { it.copy(statusFilter = event.status, page = 1) }
                loadAlerts()
            }
            is AlertQueueEvent.Search -> {
                searchQueryFlow.value = event.query
            }
            AlertQueueEvent.LoadNextPage -> {
                val currentPage = _uiState.value.page
                _uiState.update { it.copy(page = currentPage + 1) }
                loadAlerts(append = true)
            }
            AlertQueueEvent.Refresh -> {
                _uiState.update { it.copy(page = 1) }
                loadAlerts()
            }
            is AlertQueueEvent.AssignAlert -> {
                assignAlert(event.alertRef)
            }
            AlertQueueEvent.ClearAssignmentFeedback -> {
                _uiState.update { 
                    it.copy(
                        assignmentSuccess = null, 
                        assignmentError = null
                    ) 
                }
            }
        }
    }
    
    private fun loadAlerts(append: Boolean = false) {
        viewModelScope.launch {
            _uiState.update { it.copy(isLoading = true, error = null) }
            
            val state = _uiState.value
            val result = alertRepository.getAlertQueue(
                priority = state.priorityFilter,
                ownership = state.ownershipFilter,
                status = state.statusFilter,
                search = state.searchQuery.takeIf { it.isNotBlank() },
                page = state.page,
                pageSize = state.pageSize
            )
            
            result.fold(
                onSuccess = { (alerts, total) ->
                    _uiState.update { currentState ->
                        currentState.copy(
                            alerts = if (append) currentState.alerts + alerts else alerts,
                            total = total,
                            isLoading = false,
                            error = null
                        )
                    }
                },
                onFailure = { error ->
                    _uiState.update { 
                        it.copy(
                            isLoading = false, 
                            error = error.message ?: "Failed to load alerts"
                        ) 
                    }
                }
            )
        }
    }
    
    private fun assignAlert(alertRef: String) {
        viewModelScope.launch {
            val alert = _uiState.value.alerts.find { it.alertRef == alertRef }
            if (alert == null) {
                _uiState.update { 
                    it.copy(assignmentError = "Alert not found") 
                }
                return@launch
            }
            
            _uiState.update { it.copy(assigningAlertId = alertRef) }
            
            val correlationId = UUID.randomUUID().toString()
            val result = alertRepository.assignAlert(alert.alertId, correlationId)
            
            result.fold(
                onSuccess = {
                    _uiState.update { 
                        it.copy(
                            assigningAlertId = null,
                            assignmentSuccess = "Alert $alertRef assigned to you",
                            assignmentError = null
                        ) 
                    }
                    // Refresh the queue to show updated ownership
                    loadAlerts()
                },
                onFailure = { error ->
                    _uiState.update { 
                        it.copy(
                            assigningAlertId = null,
                            assignmentError = error.message ?: "Failed to assign alert"
                        ) 
                    }
                }
            )
        }
    }
}
