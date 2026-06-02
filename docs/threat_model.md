# Threat Model

## Scope

This project models risks for a synthetic internal AI agent. It does not contain real company data, customer data, employee data, credentials, or confidential workflows.

## Assets

- synthetic runbooks
- synthetic tickets
- agent prompts and policies
- retrieval index
- audit logs
- evaluation datasets

## Trust Boundaries

- User prompts are untrusted.
- Retrieved documents are untrusted.
- Tool outputs are untrusted until validated.
- Environment variables may contain secrets and must not be logged.

## Initial Risks

- prompt injection in a user message
- prompt injection embedded in retrieved documents
- unsupported claims without citations
- cross-team retrieval leakage
- unsafe side-effecting tool calls
- system prompt disclosure
- sensitive-data logging
- unbounded model or tool usage

## Initial Controls

- synthetic-only data
- citation requirements
- abstention when evidence is weak
- role-aware retrieval in later phases
- schema validation
- tool allowlist
- approval gate for side-effecting tools
- redaction for logs
- red-team evaluation cases

## Current Red-Team Coverage

The project includes deterministic red-team cases for prompt injection, grounding bypass, excessive agency, access-control bypass, retrieved-document injection, sensitive-data requests, weak evidence, tool misuse, system-prompt leakage, unbounded consumption, retrieved-context priority attacks, approval-gate bypass, citation suppression, unsupported resolution, and retrieved access escalation. The improved policy blocks these requests before retrieval or tool use, and the report assigns deterministic severity weights so weighted safe response rate and residual risk score can be tracked by risk type, attack channel, and severity band.

## Public Positioning Control

The project must not imply that it is a clone, leak, reverse-engineering attempt, or critique of any real employer system. Public materials should describe it as an independent synthetic evaluation lab for responsible internal AI agent design.
