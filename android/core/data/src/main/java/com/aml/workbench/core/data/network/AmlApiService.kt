package com.aml.workbench.core.data.network

import com.aml.workbench.core.data.network.dto.*
import retrofit2.http.*
import java.util.UUID

interface AmlApiService {
    
    @GET("/api/v1/alerts")
    suspend fun getAlertQueue(
        @Query("priority") priority: String? = null,
        @Query("ownership") ownership: String? = null,
        @Query("status") status: String? = null,
        @Query("search") search: String? = null,
        @Query("page") page: Int = 1,
        @Query("page_size") pageSize: Int = 20
    ): AlertQueueResponse
    
    @POST("/api/v1/alerts/{alertId}/assign")
    suspend fun assignAlert(
        @Path("alertId") alertId: UUID,
        @Header("X-Correlation-ID") correlationId: String
    ): AlertAssignmentResponse
    
    @GET("/api/v1/alerts/{alertId}/evidence")
    suspend fun getAlertEvidence(
        @Path("alertId") alertId: UUID
    ): AlertEvidenceDto
    
    @POST("/api/v1/cases")
    suspend fun createCase(
        @Body request: CreateCaseRequest,
        @Header("X-Correlation-ID") correlationId: String
    ): CreateCaseResponse
    
    @GET("/api/v1/alerts/{alertId}/rule-snapshots")
    suspend fun getRuleSnapshots(
        @Path("alertId") alertId: UUID
    ): List<RuleEvaluationSnapshotDto>
}
