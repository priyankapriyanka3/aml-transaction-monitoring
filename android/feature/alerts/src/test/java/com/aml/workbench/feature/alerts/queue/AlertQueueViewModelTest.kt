package com.aml.workbench.feature.alerts.queue

import app.cash.turbine.test
import com.aml.workbench.core.data.repository.AlertRepository
import com.aml.workbench.core.domain.model.Alert
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
class AlertQueueViewModelTest {
    
    private lateinit var repository: AlertRepository
    private lateinit var viewModel: AlertQueueViewModel
    private val testDispatcher = StandardTestDispatcher()
    
    @Before
    fun setup() {
        Dispatchers.setMain(testDispatcher)
        repository = mockk()
    }
    
    @After
    fun tearDown() {
        Dispatchers.resetMain()
    }
    
    @Test
    fun `initial state loads alerts with default filters`() = runTest {
        // Given
        val mockAlerts = listOf(
            Alert(
                alertId = UUID.randomUUID(),
                alertRef = "ALT-001",
                priority = "Critical",
                riskScore = 95,
                status = "New",
                ownerUserId = null,
                triggeredAtUtc = "2026-11-22T12:00:00Z",
                transactionAmount = "95000.00",
                transactionCurrencyCode = "USD",
                sourceCountryCode = "GB",
                destinationCountryCode = "VG",
                customerId = UUID.randomUUID(),
                customerName = "Test Customer"
            )
        )
        
        coEvery { 
            repository.getAlertQueue(
                priority = null,
                ownership = "Unassigned",
                status = "New",
                search = null,
                page = 1,
                pageSize = 20
            ) 
        } returns Result.success(Pair(mockAlerts, 1))
        
        // When
        viewModel = AlertQueueViewModel(repository)
        advanceUntilIdle()
        
        // Then
        viewModel.uiState.test {
            val state = awaitItem()
            assertEquals(mockAlerts, state.alerts)
            assertEquals(1, state.total)
            assertEquals(false, state.isLoading)
            assertEquals(null, state.error)
        }
    }
    
    @Test
    fun `filter by priority updates state and reloads alerts`() = runTest {
        // Given
        val mockAlerts = listOf<Alert>()
        coEvery { 
            repository.getAlertQueue(any(), any(), any(), any(), any(), any()) 
        } returns Result.success(Pair(mockAlerts, 0))
        
        viewModel = AlertQueueViewModel(repository)
        advanceUntilIdle()
        
        // When
        viewModel.onEvent(AlertQueueEvent.FilterByPriority("Critical"))
        advanceUntilIdle()
        
        // Then
        viewModel.uiState.test {
            val state = awaitItem()
            assertEquals("Critical", state.priorityFilter)
        }
    }
    
    @Test
    fun `assign alert success updates state with feedback`() = runTest {
        // Given
        val alertId = UUID.randomUUID()
        val mockAlerts = listOf(
            Alert(
                alertId = alertId,
                alertRef = "ALT-001",
                priority = "Critical",
                riskScore = 95,
                status = "New",
                ownerUserId = null,
                triggeredAtUtc = "2026-11-22T12:00:00Z",
                transactionAmount = "95000.00",
                transactionCurrencyCode = "USD",
                sourceCountryCode = "GB",
                destinationCountryCode = "VG",
                customerId = UUID.randomUUID(),
                customerName = "Test Customer"
            )
        )
        
        coEvery { 
            repository.getAlertQueue(any(), any(), any(), any(), any(), any()) 
        } returns Result.success(Pair(mockAlerts, 1))
        
        coEvery { 
            repository.assignAlert(alertId, any()) 
        } returns Result.success(Unit)
        
        viewModel = AlertQueueViewModel(repository)
        advanceUntilIdle()
        
        // When
        viewModel.onEvent(AlertQueueEvent.AssignAlert("ALT-001"))
        advanceUntilIdle()
        
        // Then
        viewModel.uiState.test {
            val state = awaitItem()
            assertEquals("Alert ALT-001 assigned to you", state.assignmentSuccess)
            assertEquals(null, state.assignmentError)
        }
    }
}
