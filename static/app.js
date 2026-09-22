document.addEventListener('DOMContentLoaded', () => {
    const loanForm = document.getElementById('loan-form');
    const btnSubmit = document.getElementById('btn-submit');
    const btnLoadPrime = document.getElementById('btn-load-prime');
    const btnLoadRisk = document.getElementById('btn-load-risk');
    const btnCopyMemo = document.getElementById('btn-copy-memo');
    const memoOutput = document.getElementById('memo-output');
    const metricsHud = document.getElementById('metrics-hud');

    // Agent Nodes
    const nodePii = document.getElementById('node-pii');
    const nodeKyc = document.getElementById('node-kyc');
    const nodeRisk = document.getElementById('node-risk');
    const nodeDecision = document.getElementById('node-decision');

    function setNodeStatus(node, statusText, statusClass) {
        node.className = `agent-node ${statusClass}`;
        const statusEl = node.querySelector('.node-status');
        statusEl.textContent = statusText;
        statusEl.className = `node-status status-${statusClass.replace('active', 'running').replace('completed', 'passed')}`;
    }

    function resetPipelineVisuals() {
        [nodePii, nodeKyc, nodeRisk, nodeDecision].forEach(node => {
            node.className = 'agent-node';
            const statusEl = node.querySelector('.node-status');
            statusEl.textContent = 'Ready';
            statusEl.className = 'node-status status-ready';
        });
    }

    // Load Sample Profile
    async function loadSample(type) {
        try {
            const res = await fetch(`/api/v1/samples/${type}`);
            if (!res.ok) throw new Error("Failed to load sample");
            const data = await res.json();

            document.getElementById('applicant_id').value = data.applicant_id || '';
            document.getElementById('full_name').value = data.full_name || '';
            document.getElementById('national_id').value = data.national_id || '';
            document.getElementById('phone').value = data.phone || '';
            document.getElementById('email').value = data.email || '';
            document.getElementById('date_of_birth').value = data.date_of_birth || '';
            document.getElementById('employer_name').value = data.employer_name || '';
            document.getElementById('years_employed').value = data.years_employed || 1;
            document.getElementById('monthly_gross_income').value = data.monthly_gross_income || 0;
            document.getElementById('existing_monthly_debt_obligations').value = data.existing_monthly_debt_obligations || 0;
            document.getElementById('credit_score').value = data.credit_score || 600;
            document.getElementById('unresolved_bounces_count').value = data.bank_statement_summary?.unresolved_bounces_count || 0;
            document.getElementById('requested_loan_amount').value = data.requested_loan_amount || 5000;
            document.getElementById('loan_tenure_months').value = data.loan_tenure_months || 24;

            resetPipelineVisuals();
            memoOutput.innerHTML = `<p class="placeholder-text">Loaded sample: <strong>${data.full_name} (${type.toUpperCase()})</strong>. Click Execute to start underwriting.</p>`;
            metricsHud.style.display = 'none';
        } catch (err) {
            alert("Error loading sample data: " + err.message);
        }
    }

    btnLoadPrime.addEventListener('click', () => loadSample('prime'));
    btnLoadRisk.addEventListener('click', () => loadSample('high_risk'));

    // Handle Form Submission
    loanForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        btnSubmit.disabled = true;
        btnSubmit.textContent = "⏳ Agents Negotiating Decision...";
        resetPipelineVisuals();

        const payload = {
            applicant_id: document.getElementById('applicant_id').value,
            full_name: document.getElementById('full_name').value,
            national_id: document.getElementById('national_id').value,
            phone: document.getElementById('phone').value,
            email: document.getElementById('email').value,
            date_of_birth: document.getElementById('date_of_birth').value,
            employment_type: "Salaried Full-time",
            employer_name: document.getElementById('employer_name').value,
            years_employed: parseFloat(document.getElementById('years_employed').value),
            requested_loan_amount: parseFloat(document.getElementById('requested_loan_amount').value),
            loan_purpose: "Personal Banking Credit Facility",
            loan_tenure_months: parseInt(document.getElementById('loan_tenure_months').value),
            credit_score: parseInt(document.getElementById('credit_score').value),
            monthly_gross_income: parseFloat(document.getElementById('monthly_gross_income').value),
            existing_monthly_debt_obligations: parseFloat(document.getElementById('existing_monthly_debt_obligations').value),
            bank_statement_summary: {
                average_monthly_balance: parseFloat(document.getElementById('monthly_gross_income').value) * 0.4,
                unresolved_bounces_count: parseInt(document.getElementById('unresolved_bounces_count').value)
            }
        };

        // Step 1: PII Sanitizer Animation
        setNodeStatus(nodePii, 'Sanitizing...', 'active');
        await new Promise(r => setTimeout(r, 400));
        setNodeStatus(nodePii, 'Redacted', 'completed');

        // Step 2: KYC Agent Animation
        setNodeStatus(nodeKyc, 'Verifying KYC...', 'active');
        await new Promise(r => setTimeout(r, 400));

        try {
            const response = await fetch('/api/v1/underwrite', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload)
            });

            if (!response.ok) throw new Error("API Server returned error");
            const result = await response.json();

            // Complete KYC status
            setNodeStatus(nodeKyc, result.kyc_status, result.kyc_status === 'REJECTED' ? 'failed' : 'completed');

            // Step 3: Risk & RAG Agent
            setNodeStatus(nodeRisk, 'Policy RAG...', 'active');
            await new Promise(r => setTimeout(r, 400));
            setNodeStatus(nodeRisk, `Risk: ${result.risk_level}`, result.risk_level === 'HIGH' ? 'failed' : 'completed');

            // Step 4: Decision Agent
            setNodeStatus(nodeDecision, 'Deciding...', 'active');
            await new Promise(r => setTimeout(r, 400));
            setNodeStatus(nodeDecision, result.final_decision, result.final_decision === 'REJECTED' ? 'failed' : 'completed');

            // Update Metrics HUD
            metricsHud.style.display = 'grid';
            const verdictEl = document.getElementById('metric-verdict');
            verdictEl.textContent = result.final_decision;
            verdictEl.className = `metric-val verdict-${result.final_decision.toLowerCase().replace('_', '-')}`;

            document.getElementById('metric-amount').textContent = `$${result.approved_amount.toLocaleString()}`;
            document.getElementById('metric-rate').textContent = `${result.approved_interest_rate}% p.a.`;
            document.getElementById('metric-dti').textContent = `${result.financial_metrics?.dti_percentage || 0}%`;

            // Display Memo
            memoOutput.textContent = result.decision_memo_markdown;

        } catch (err) {
            alert("Error in execution: " + err.message);
        } finally {
            btnSubmit.disabled = false;
            btnSubmit.textContent = "⚡ Execute Autonomous Underwriting Workflow";
        }
    });

    // Copy Memo
    btnCopyMemo.addEventListener('click', () => {
        const text = memoOutput.textContent;
        if (!text || text.includes('Load an applicant profile')) return;
        navigator.clipboard.writeText(text);
        btnCopyMemo.textContent = "Copied! ✓";
        setTimeout(() => { btnCopyMemo.textContent = "Copy Memo"; }, 2000);
    });
});
