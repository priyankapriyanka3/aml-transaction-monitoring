package com.aml.workbench.core.data.network.dto

import com.google.gson.annotations.SerializedName
import java.util.UUID

data class AlertQueueResponse(
    @SerializedName("items") val items: List<AlertQueueItemDto>,
    @SerializedName("total") val total: Int,
    @SerializedName("page") val page: Int,
    @SerializedName("page_size") val pageSize: Int
)

data class AlertQueueItemDto(
    @SerializedName("alert_id") val alertId: UUID,
    @SerializedName("alert_ref") val alertRef: String,
    @SerializedName("priority") val priority: String,
    @SerializedName("risk_score") val riskScore: Int,
    @SerializedName("status") val status: String,
    @SerializedName("owner_user_id") val ownerUserId: UUID?,
    @SerializedName("triggered_at_utc") val triggeredAtUtc: String,
    @SerializedName("transaction_amount") val transactionAmount: String,
    @SerializedName("transaction_currency_code") val transactionCurrencyCode: String,
    @SerializedName("source_country_code") val sourceCountryCode: String,
    @SerializedName("destination_country_code") val destinationCountryCode: String,
    @SerializedName("customer_id") val customerId: UUID,
    @SerializedName("customer_name") val customerName: String
)

data class AlertAssignmentResponse(
    @SerializedName("alert_id") val alertId: UUID,
    @SerializedName("owner_user_id") val ownerUserId: UUID,
    @SerializedName("assigned_at_utc") val assignedAtUtc: String
)

data class AlertEvidenceDto(
    @SerializedName("alert_id") val alertId: UUID,
    @SerializedName("alert_ref") val alertRef: String,
    @SerializedName("priority") val priority: String,
    @SerializedName("risk_score") val riskScore: Int,
    @SerializedName("status") val status: String,
    @SerializedName("triggered_at_utc") val triggeredAtUtc: String,
    @SerializedName("transaction") val transaction: TransactionFactsDto,
    @SerializedName("customer") val customer: CustomerContextDto,
    @SerializedName("account") val account: AccountContextDto
)

data class TransactionFactsDto(
    @SerializedName("transaction_id") val transactionId: UUID,
    @SerializedName("transaction_ref") val transactionRef: String,
    @SerializedName("amount") val amount: String,
    @SerializedName("currency_code") val currencyCode: String,
    @SerializedName("source_country_code") val sourceCountryCode: String,
    @SerializedName("destination_country_code") val destinationCountryCode: String,
    @SerializedName("executed_at_utc") val executedAtUtc: String
)

data class CustomerContextDto(
    @SerializedName("customer_id") val customerId: UUID,
    @SerializedName("customer_name") val customerName: String,
    @SerializedName("pep_flag") val pepFlag: Boolean,
    @SerializedName("country_code") val countryCode: String
)

data class AccountContextDto(
    @SerializedName("account_id") val accountId: UUID,
    @SerializedName("account_ref") val accountRef: String,
    @SerializedName("account_type") val accountType: String
)

data class CreateCaseRequest(
    @SerializedName("alert_id") val alertId: UUID
)

data class CreateCaseResponse(
    @SerializedName("case_id") val caseId: UUID,
    @SerializedName("case_ref") val caseRef: String,
    @SerializedName("primary_alert_id") val primaryAlertId: UUID,
    @SerializedName("created_by_user_id") val createdByUserId: UUID,
    @SerializedName("status") val status: String,
    @SerializedName("created_at_utc") val createdAtUtc: String
)

data class RuleEvaluationSnapshotDto(
    @SerializedName("snapshot_id") val snapshotId: UUID,
    @SerializedName("alert_id") val alertId: UUID,
    @SerializedName("rule_code") val ruleCode: String,
    @SerializedName("rule_name") val ruleName: String,
    @SerializedName("rule_version") val ruleVersion: String,
    @SerializedName("outcome") val outcome: String,
    @SerializedName("condition_text") val conditionText: String,
    @SerializedName("evaluated_from_utc") val evaluatedFromUtc: String,
    @SerializedName("evaluated_to_utc") val evaluatedToUtc: String
)
