package com.aml.workbench.feature.alerts.evidence

import androidx.lifecycle.SavedStateHandle
import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.aml.workbench.core.data.repository.AlertRepository
import dagger.hilt.android.lifecycle.HiltViewModel
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.flow.update
import kotlinx.coroutines.launch
import java.util.UUID
import javax.inject.Inject

@HiltViewModel
class EvidenceViewModel @Inject constructor(
    savedStateHandle: SavedStateHandle,
    private val alertRepository: AlertRepository
) : ViewModel() {
    
    private val alertId: UUID = UUID.fromString(
        savedStateHandle.get<String>("alertId") 
            ?: throw IllegalArgumentException("alertId is required")
    )
    
    private val _uiState = MutableStateFlow(EvidenceUiState())
    val uiState: StateFlow<EvidenceUiState> = _uiState.asStateFlow()
    
    init {
        loadEvidence()
    }
    
    fun onEvent(event: EvidenceEvent) {
        when (event) {
            EvidenceEvent.CreateCase -> createCase()
            EvidenceEvent.Retry -> loadEvidence()
            EvidenceEvent.ClearCaseCreationFeedback -> {
                _uiState.update { 
                    it.copy(caseCreated = null, caseCreationError = null) 
                }
            }
        }
    }
    
    private fun loadEvidence() {
        viewModelScope.launch {
            _uiState.update { it.copy(isLoading = true, error = null) }
            
            val result = alertRepository.getAlertEvidence(alertId)
            
            result.fold(
                onSuccess = { evidence ->
                    _uiState.update { 
                        it.copy(
                            evidence = evidence,
                            isLoading = false,
                            error = null
                        ) 
                    }
                },
                onFailure = { error ->
                    _uiState.update { 
                        it.copy(
                            isLoading = false,
                            error = error.message ?: "Failed to load evidence"
                        ) 
                    }
                }
            )
        }
    }
    
    private fun createCase() {
        viewModelScope.launch {
            _uiState.update { it.copy(isCreatingCase = true) }
            
            val correlationId = UUID.randomUUID().toString()
            val result = alertRepository.createCase(alertId, correlationId)
            
            result.fold(
                onSuccess = { caseRef ->
                    _uiState.update { 
                        it.copy(
                            isCreatingCase = false,
                            caseCreated = caseRef,
                            caseCreationError = null
                        ) 
                    }
                },
                onFailure = { error ->
                    _uiState.update { 
                        it.copy(
                            isCreatingCase = false,
                            caseCreationError = error.message ?: "Failed to create case"
                        ) 
                    }
                }
            )
        }
    }
}
