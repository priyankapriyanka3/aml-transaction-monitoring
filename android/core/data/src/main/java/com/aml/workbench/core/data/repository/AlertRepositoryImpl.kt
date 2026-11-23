package com.aml.workbench.core.data.repository

import com.aml.workbench.core.data.network.AmlApiService
import com.aml.workbench.core.data.network.dto.*
import com.aml.workbench.core.domain.model.*
import java.util.UUID
import javax.inject.Inject
import javax.inject.Singleton

interface AlertRepository {
    suspend fun getAlertQueue(
        priority: String? = null,
        ownership: String? = null,
        status: String? = null,
        search: String? = null,
        page: Int = 1,
        pageSize: Int = 20
    ): Result<Pair<List<Alert>, Int>>
    
    suspend fun assignAlert(alertId: UUID, correlationId: String): Result<Unit>
    
    suspend fun getAlertEvidence(alertId: UUID): Result<AlertEvidence>
    
    suspend fun createCase(alertId: UUID, correlationId: String): Result<String>
}

@Singleton
class AlertRepositoryImpl @Inject constructor(
    private val apiService: AmlApiService
) : AlertRepository {
    
    override suspend fun getAlertQueue(
        priority: String?,
        ownership: String?,
        status: String?,
        search: String?,
        page: Int,
        pageSize: Int
    ): Result<Pair<List<Alert>, Int>> = runCatching {
        val response = apiService.getAlertQueue(
            priority = priority,
            ownership = ownership,
            status = status,
            search = search,
            page = page,
            pageSize = pageSize
        )
        
        val alerts = response.items.map { it.toDomain() }
        Pair(alerts, response.total)
    }
    
    override suspend fun assignAlert(alertId: UUID, correlationId: String): Result<Unit> = runCatching {
        apiService.assignAlert(alertId, correlationId)
        Unit
    }
    
    override suspend fun getAlertEvidence(alertId: UUID): Result<AlertEvidence> = runCatching {
        apiService.getAlertEvidence(alertId).toDomain()
    }
    
    override suspend fun createCase(alertId: UUID, correlationId: String): Result<String> = runCatching {
        val response = apiService.createCase(
            CreateCaseRequest(alertId),
            correlationId
        )
        response.caseRef
    }
}

private fun AlertQueueItemDto.toDomain() = Alert(
    alertId = alertId,
    alertRef = alertRef,
    priority = priority,
    riskScore = riskScore,
    status = status,
    ownerUserId = ownerUserId,
    triggeredAtUtc = triggeredAtUtc,
    transactionAmount = transactionAmount,
    transactionCurrencyCode = transactionCurrencyCode,
    sourceCountryCode = sourceCountryCode,
    destinationCountryCode = destinationCountryCode,
    customerId = customerId,
    customerName = customerName
)

private fun AlertEvidenceDto.toDomain() = AlertEvidence(
    alertId = alertId,
    alertRef = alertRef,
    priority = priority,
    riskScore = riskScore,
    status = status,
    triggeredAtUtc = triggeredAtUtc,
    transaction = transaction.toDomain(),
    customer = customer.toDomain(),
    account = account.toDomain()
)

private fun TransactionFactsDto.toDomain() = TransactionFacts(
    transactionId = transactionId,
    transactionRef = transactionRef,
    amount = amount,
    currencyCode = currencyCode,
    sourceCountryCode = sourceCountryCode,
    destinationCountryCode = destinationCountryCode,
    executedAtUtc = executedAtUtc
)

private fun CustomerContextDto.toDomain() = CustomerContext(
    customerId = customerId,
    customerName = customerName,
    pepFlag = pepFlag,
    countryCode = countryCode
)

private fun AccountContextDto.toDomain() = AccountContext(
    accountId = accountId,
    accountRef = accountRef,
    accountType = accountType
)
