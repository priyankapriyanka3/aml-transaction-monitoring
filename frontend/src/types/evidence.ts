// Evidence types matching backend EvidencePackageResponse schema

export interface CustomerContext {
  customer_id: string;
  customer_name: string;
  onboarding_profile: string;
  risk_classification: string;
  exposure_indicators_json: string;
  risk_rating: string | null;
  kyc_review_date: string | null;
  pep_flag: boolean;
  sanctions_flag: boolean;
  adverse_media_flag: boolean;
}

export interface AccountRelationship {
  account_id: string;
  customer_id: string;
  account_number_masked: string;
  relationship_type: string;
  jurisdiction_code: string;
  product_type: string;
}

export interface TransactionEvidence {
  transaction_id: string;
  customer_id: string;
  account_id: string;
  booked_at: string;
  amount: number;
  currency: string;
  counterparty_name: string | null;
  corridor: string;
  generation_source: string;
  linked_alert_id: string | null;
}

export interface RuleEvaluation {
  rule_evaluation_id: string;
  alert_id: string;
  rule_code: string;
  rule_name: string;
  rule_version: string;
  outcome: 'MATCH' | 'PASS';
  threshold_explanation: string;
  evaluated_at: string;
}

export interface EvidencePackage {
  case_id: string;
  customer: CustomerContext;
  accounts: AccountRelationship[];
  transactions: TransactionEvidence[];
  rule_evaluations: RuleEvaluation[];
  evidence_locked_for_review: boolean;
}
