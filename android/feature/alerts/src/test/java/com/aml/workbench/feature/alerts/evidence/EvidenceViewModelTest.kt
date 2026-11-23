package com.aml.workbench.feature.alerts.evidence

import androidx.lifecycle.SavedStateHandle
import app.cash.turbine.test
import com.aml.workbench.core.data.repository.AlertRepository
import com.aml.workbench.core.domain.model.*
import io.mockk.coEvery
import io.mockk.mockk
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.ExperimentalCoroutinesApi
import kotlinx.coroutines.test.*
import org.junit.After
import org.junit.Assert.assertEquals
import org.junit.Before
import org.junit.Test
import java.util.UUID

@OptIn(ExperimentalCoroutinesApi::class)
class EvidenceViewModelTest {
    
    private lateinit var repository: AlertRepository
    private lateinit var viewModel: EvidenceViewModel
    private lateinit var savedStateHandle: SavedStateHandle
    private val testDispatcher = StandardTestDispatcher()
    private val testAlertId = UUID.randomUUID()
    
    @Before
    fun setup() {
        Dispatchers.setMain(testDispatcher)
        repository = mockk()
        savedStateHandle = SavedStateHandle(mapOf("alertId" to testAlertId.toString()))
    }
    
    @After
    fun tearDown() {
        Dispatchers.resetMain()
    }
    
    @Test
    fun `initial load fetches evidence successfully`() = runTest {
        // Given
        val mockEvidence = AlertEvidence(
            alertId = testAlertId,
            alertRef = "ALT-001",
            priority = "Critical",
            riskScore = 95,
            status = "New",
            triggeredAtUtc = "2026-11-22T12:00:00Z",
            transaction = TransactionFacts(
                transactionId = UUID.randomUUID(),
                transactionRef = "TX-001",
                amount = "95000.00",
                currencyCode = "USD",
                sourceCountryCode = "GB",
                destinationCountryCode = "VG",
                executedAtUtc = "2026-11-22T12:00:00Z"
            ),
            customer = CustomerContext(
                customerId = UUID.randomUUID(),
                customerName = "Test Customer",
                pepFlag = false,
                countryCode = "GB"
            ),
            account = AccountContext(
                accountId = UUID.randomUUID(),
                accountRef = "ACC-001",
                accountType = "Current"
            )
        )
        
        coEvery { 
            repository.getAlertEvidence(testAlertId) 
        } returns Result.success(mockEvidence)
        
        // When
        viewModel = EvidenceViewModel(savedStateHandle, repository)
        advanceUntilIdle()
        
        // Then
        viewModel.uiState.test {
            val state = awaitItem()
            assertEquals(mockEvidence, state.evidence)
            assertEquals(false, state.isLoading)
            assertEquals(null, state.error)
        }
    }
    
    @Test
    fun `create case success returns case reference`() = runTest {
        // Given
        val mockEvidence = AlertEvidence(
            alertId = testAlertId,
            alertRef = "ALT-001",
            priority = "Critical",
            riskScore = 95,
            status = "New",
            triggeredAtUtc = "2026-11-22T12:00:00Z",
            transaction = TransactionFacts(
                transactionId = UUID.randomUUID(),
                transactionRef = "TX-001",
                amount = "95000.00",
                currencyCode = "USD",
                sourceCountryCode = "GB",
                destinationCountryCode = "VG",
                executedAtUtc = "2026-11-22T12:00:00Z"
            ),
            customer = CustomerContext(
                customerId = UUID.randomUUID(),
                customerName = "Test Customer",
                pepFlag = false,
                countryCode = "GB"
            ),
            account = AccountContext(
                accountId = UUID.randomUUID(),
                accountRef = "ACC-001",
                accountType = "Current"
            )
        )
        
        coEvery { 
            repository.getAlertEvidence(testAlertId) 
        } returns Result.success(mockEvidence)
        
        coEvery { 
            repository.createCase(testAlertId, any()) 
        } returns Result.success("CS-204")
        
        viewModel = EvidenceViewModel(savedStateHandle, repository)
        advanceUntilIdle()
        
        // When
        viewModel.onEvent(EvidenceEvent.CreateCase)
        advanceUntilIdle()
        
        // Then
        viewModel.uiState.test {
            val state = awaitItem()
            assertEquals("CS-204", state.caseCreated)
            assertEquals(false, state.isCreatingCase)
            assertEquals(null, state.caseCreationError)
        }
    }
    
    @Test
    fun `evidence load failure updates error state`() = runTest {
        // Given
        val errorMessage = "Network error"
        coEvery { 
            repository.getAlertEvidence(testAlertId) 
        } returns Result.failure(Exception(errorMessage))
        
        // When
        viewModel = EvidenceViewModel(savedStateHandle, repository)
        advanceUntilIdle()
        
        // Then
        viewModel.uiState.test {
            val state = awaitItem()
            assertEquals(null, state.evidence)
            assertEquals(false, state.isLoading)
            assertEquals(errorMessage, state.error)
        }
    }
}
