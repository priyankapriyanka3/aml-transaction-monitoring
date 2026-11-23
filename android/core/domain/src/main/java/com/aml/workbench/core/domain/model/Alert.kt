package com.aml.workbench.core.domain.model

import java.util.UUID

data class Alert(
    val alertId: UUID,
    val alertRef: String,
    val priority: String,
    val riskScore: Int,
    val status: String,
    val ownerUserId: UUID?,
    val triggeredAtUtc: String,
    val transactionAmount: String,
    val transactionCurrencyCode: String,
    val sourceCountryCode: String,
    val destinationCountryCode: String,
    val customerId: UUID,
    val customerName: String
)

data class AlertEvidence(
    val alertId: UUID,
    val alertRef: String,
    val priority: String,
    val riskScore: Int,
    val status: String,
    val triggeredAtUtc: String,
    val transaction: TransactionFacts,
    val customer: CustomerContext,
    val account: AccountContext
)

data class TransactionFacts(
    val transactionId: UUID,
    val transactionRef: String,
    val amount: String,
    val currencyCode: String,
    val sourceCountryCode: String,
    val destinationCountryCode: String,
    val executedAtUtc: String
)

data class CustomerContext(
    val customerId: UUID,
    val customerName: String,
    val pepFlag: Boolean,
    val countryCode: String
)

data class AccountContext(
    val accountId: UUID,
    val accountRef: String,
    val accountType: String
)

data class RuleEvaluationSnapshot(
    val snapshotId: UUID,
    val alertId: UUID,
    val ruleCode: String,
    val ruleName: String,
    val ruleVersion: String,
    val outcome: String,
    val conditionText: String,
    val evaluatedFromUtc: String,
    val evaluatedToUtc: String
)
