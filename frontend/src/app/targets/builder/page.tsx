"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import { 
  createTarget, 
  TargetCreatePayload, 
  OpportunityType 
} from "@/lib/target-api";
import { 
  ArrowLeft, 
  ArrowRight, 
  Check, 
  Sparkles, 
  Target, 
  Layers, 
  MapPin, 
  DollarSign, 
  Users, 
  Code, 
  Globe, 
  AlertCircle,
  FileText,
  ShieldCheck
} from "lucide-react";

export default function TargetBuilderWizardPage() {
  const router = useRouter();
  const queryClient = useQueryClient();
  const [currentStep, setCurrentStep] = useState<number>(1);
  const [validationError, setValidationError] = useState<string | null>(null);

  // Form State
  const [name, setName] = useState("");
  const [niche, setNiche] = useState("");
  const [subNiche, setSubNiche] = useState("");
  const [geography, setGeography] = useState("");

  const [opportunityTypes, setOpportunityTypes] = useState<OpportunityType[]>([
    "NEW_WEBSITE",
    "SEO",
  ]);

  const [enabledSources, setEnabledSources] = useState<string[]>([
    "google_places",
    "website_crawler",
    "social_discovery",
  ]);

  const [minRevenue, setMinRevenue] = useState<string>("");
  const [maxRevenue, setMaxRevenue] = useState<string>("");
  const [minEmployees, setMinEmployees] = useState<string>("");
  const [maxEmployees, setMaxEmployees] = useState<string>("");
  const [technologiesInput, setTechnologiesInput] = useState("WordPress, React, Shopify");
  const [keywordsInput, setKeywordsInput] = useState("commercial, B2B, service");
  const [maxResultsLimit, setMaxResultsLimit] = useState<number>(100);

  // Create Target Mutation
  const createMutation = useMutation({
    mutationFn: (payload: TargetCreatePayload) => createTarget(payload),
    onSuccess: (newTarget) => {
      queryClient.invalidateQueries({ queryKey: ["targets"] });
      router.push(`/targets/${newTarget.id}`);
    },
    onError: (err: any) => {
      setValidationError(err.message || "Failed to create target campaign.");
    },
  });

  // Step Validation logic
  const validateStep = (step: number): boolean => {
    setValidationError(null);

    if (step === 1) {
      if (!name.trim() || name.trim().length < 3) {
        setValidationError("Campaign Name must be at least 3 characters long.");
        return false;
      }
      if (!niche.trim() || niche.trim().length < 2) {
        setValidationError("Target Niche must be at least 2 characters long.");
        return false;
      }
      if (!geography.trim() || geography.trim().length < 2) {
        setValidationError("Geography / Target Location must be specified.");
        return false;
      }
    }

    if (step === 2) {
      if (opportunityTypes.length === 0) {
        setValidationError("Please select at least one sales opportunity type.");
        return false;
      }
    }

    if (step === 3) {
      const minRev = minRevenue ? parseFloat(minRevenue) : null;
      const maxRev = maxRevenue ? parseFloat(maxRevenue) : null;
      const minEmp = minEmployees ? parseInt(minEmployees, 10) : null;
      const maxEmp = maxEmployees ? parseInt(maxEmployees, 10) : null;

      if (minRev !== null && minRev < 0) {
        setValidationError("Minimum revenue cannot be negative.");
        return false;
      }
      if (maxRev !== null && maxRev < 0) {
        setValidationError("Maximum revenue cannot be negative.");
        return false;
      }
      if (minRev !== null && maxRev !== null && minRev > maxRev) {
        setValidationError("Minimum revenue cannot be greater than maximum revenue.");
        return false;
      }

      if (minEmp !== null && minEmp < 0) {
        setValidationError("Minimum employee count cannot be negative.");
        return false;
      }
      if (maxEmp !== null && maxEmp < 0) {
        setValidationError("Maximum employee count cannot be negative.");
        return false;
      }
      if (minEmp !== null && maxEmp !== null && minEmp > maxEmp) {
        setValidationError("Minimum employee count cannot be greater than maximum employee count.");
        return false;
      }
    }

    return true;
  };

  const handleNext = () => {
    if (validateStep(currentStep)) {
      setCurrentStep((prev) => Math.min(prev + 1, 4));
    }
  };

  const handleBack = () => {
    setValidationError(null);
    setCurrentStep((prev) => Math.max(prev - 1, 1));
  };

  const handleSubmit = () => {
    if (!validateStep(1) || !validateStep(2) || !validateStep(3)) {
      return;
    }

    const payload: TargetCreatePayload = {
      name: name.trim(),
      niche: niche.trim(),
      sub_niche: subNiche.trim() || undefined,
      geography: geography.trim(),
      opportunity_types: opportunityTypes,
      filters: {
        min_revenue: minRevenue ? parseFloat(minRevenue) : null,
        max_revenue: maxRevenue ? parseFloat(maxRevenue) : null,
        min_employees: minEmployees ? parseInt(minEmployees, 10) : null,
        max_employees: maxEmployees ? parseInt(maxEmployees, 10) : null,
        technologies: technologiesInput.split(",").map((s) => s.trim()).filter(Boolean),
        keywords: keywordsInput.split(",").map((s) => s.trim()).filter(Boolean),
      },
      source_configuration: {
        enabled_sources: enabledSources,
        max_results_limit: maxResultsLimit,
        rate_limit_per_minute: 60,
        timeout_seconds: 30.0,
      },
    };

    createMutation.mutate(payload);
  };

  const toggleOpportunity = (type: OpportunityType) => {
    if (opportunityTypes.includes(type)) {
      setOpportunityTypes(opportunityTypes.filter((t) => t !== type));
    } else {
      setOpportunityTypes([...opportunityTypes, type]);
    }
  };

  const steps = [
    { number: 1, title: "01 Definition", desc: "Niche & Location" },
    { number: 2, title: "02 Opportunities & Sources", desc: "Sales Signals & Limits" },
    { number: 3, title: "03 Lead Filters", desc: "Revenue & Employees" },
    { number: 4, title: "04 Review & Launch", desc: "Final Review" },
  ];

  return (
    <div className="space-y-8 max-w-4xl mx-auto">
      {/* Top Header */}
      <div className="bg-white p-6 rounded-2xl border border-slate-200 shadow-card-sm flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2">
            <span className="px-3 py-1 rounded-full text-xs font-semibold bg-indigo-50 text-indigo-700 border border-indigo-200">
              4-Step Guided Wizard
            </span>
            <span className="text-xs text-slate-500 font-medium">Target Builder</span>
          </div>
          <h1 className="text-2xl font-extrabold text-slate-900 tracking-tight font-display mt-1">
            Create Target Campaign
          </h1>
        </div>

        <button
          onClick={() => router.push("/targets")}
          className="flex items-center gap-2 px-3.5 py-2 rounded-xl bg-slate-100 hover:bg-slate-200 text-slate-700 font-semibold text-xs border border-slate-200 transition self-start md:self-auto"
        >
          <ArrowLeft className="w-4 h-4" />
          <span>Back to Directory</span>
        </button>
      </div>

      {/* Wizard Progress Bar */}
      <div className="bg-white p-4 rounded-2xl border border-slate-200 shadow-card-sm">
        <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
          {steps.map((step) => {
            const isCompleted = currentStep > step.number;
            const isCurrent = currentStep === step.number;

            return (
              <div
                key={step.number}
                className={`p-3 rounded-xl border flex items-center gap-3 transition ${
                  isCurrent
                    ? "bg-indigo-50 border-indigo-200 text-indigo-900 shadow-xs"
                    : isCompleted
                    ? "bg-emerald-50/60 border-emerald-200 text-emerald-900"
                    : "bg-slate-50 border-slate-200 text-slate-400"
                }`}
              >
                <div
                  className={`w-8 h-8 rounded-lg flex items-center justify-center font-bold text-xs shrink-0 ${
                    isCurrent
                      ? "bg-indigo-600 text-white"
                      : isCompleted
                      ? "bg-emerald-600 text-white"
                      : "bg-slate-200 text-slate-500"
                  }`}
                >
                  {isCompleted ? <Check className="w-4 h-4" /> : step.number}
                </div>
                <div className="min-w-0">
                  <h4 className="font-bold text-xs tracking-tight truncate font-display">
                    {step.title}
                  </h4>
                  <span className="text-[10px] text-slate-500 block truncate">
                    {step.desc}
                  </span>
                </div>
              </div>
            );
          })}
        </div>
      </div>

      {/* Validation Error Banner */}
      {validationError && (
        <div className="p-4 rounded-xl bg-rose-50 border border-rose-200 text-rose-800 flex items-center gap-3 text-sm">
          <AlertCircle className="w-5 h-5 text-rose-600 shrink-0" />
          <span>{validationError}</span>
        </div>
      )}

      {/* Step Content Card */}
      <div className="bg-white p-6 md:p-8 rounded-2xl border border-slate-200 shadow-card-sm space-y-6">
        {/* STEP 1: Definition */}
        {currentStep === 1 && (
          <div className="space-y-6">
            <div>
              <h2 className="text-lg font-bold text-slate-900 font-display flex items-center gap-2">
                <FileText className="w-5 h-5 text-indigo-600" />
                <span>Step 1: Campaign Definition</span>
              </h2>
              <p className="text-xs text-slate-500 mt-1">
                Define basic target identification parameters and geographic boundaries.
              </p>
            </div>

            <div className="space-y-4">
              <div>
                <label className="block text-xs font-semibold text-slate-700 mb-1">
                  Campaign Title <span className="text-rose-500">*</span>
                </label>
                <input
                  type="text"
                  placeholder="e.g. Austin Commercial Dental Clinics 2026"
                  value={name}
                  onChange={(e) => setName(e.target.value)}
                  className="w-full px-4 py-2.5 rounded-xl border border-slate-200 bg-slate-50 text-sm text-slate-900 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:bg-white"
                />
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="block text-xs font-semibold text-slate-700 mb-1">
                    Primary Niche <span className="text-rose-500">*</span>
                  </label>
                  <input
                    type="text"
                    placeholder="e.g. Dental Clinics, HVAC Services, Law Firms"
                    value={niche}
                    onChange={(e) => setNiche(e.target.value)}
                    className="w-full px-4 py-2.5 rounded-xl border border-slate-200 bg-slate-50 text-sm text-slate-900 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:bg-white"
                  />
                </div>

                <div>
                  <label className="block text-xs font-semibold text-slate-700 mb-1">
                    Sub-Niche (Optional)
                  </label>
                  <input
                    type="text"
                    placeholder="e.g. Pediatric Dentistry, Orthodontics"
                    value={subNiche}
                    onChange={(e) => setSubNiche(e.target.value)}
                    className="w-full px-4 py-2.5 rounded-xl border border-slate-200 bg-slate-50 text-sm text-slate-900 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:bg-white"
                  />
                </div>
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-700 mb-1">
                  Geography / Target Region <span className="text-rose-500">*</span>
                </label>
                <input
                  type="text"
                  placeholder="e.g. Austin, Texas, USA"
                  value={geography}
                  onChange={(e) => setGeography(e.target.value)}
                  className="w-full px-4 py-2.5 rounded-xl border border-slate-200 bg-slate-50 text-sm text-slate-900 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:bg-white"
                />
              </div>
            </div>
          </div>
        )}

        {/* STEP 2: Opportunities & Sources */}
        {currentStep === 2 && (
          <div className="space-y-6">
            <div>
              <h2 className="text-lg font-bold text-slate-900 font-display flex items-center gap-2">
                <Sparkles className="w-5 h-5 text-indigo-600" />
                <span>Step 2: Sales Opportunity Signals & Data Limits</span>
              </h2>
              <p className="text-xs text-slate-500 mt-1">
                Select targeted opportunity signals and target discovery limit per campaign run.
              </p>
            </div>

            <div className="space-y-4">
              <label className="block text-xs font-semibold text-slate-700">
                Targeted Opportunity Signals <span className="text-rose-500">*</span>
              </label>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                {[
                  { id: "NEW_WEBSITE", label: "Missing Website", desc: "Businesses operating without a digital domain" },
                  { id: "WEBSITE_REDESIGN", label: "Website Redesign", desc: "Outdated website design or unoptimized UI" },
                  { id: "SEO", label: "Organic Search SEO", desc: "Low domain authority, missing meta title tags" },
                  { id: "LOCAL_SEO", label: "Local Maps & GMB SEO", desc: "Unclaimed GMB profile or weak local citations" },
                  { id: "SOCIAL_TO_WEBSITE", label: "Social to Website Gap", desc: "Active social accounts with no official website" },
                  { id: "CONVERSION_OPTIMIZATION", label: "Conversion Optimization", desc: "Poor conversion funnel or missing booking form" },
                ].map((opp) => {
                  const selected = opportunityTypes.includes(opp.id as OpportunityType);
                  return (
                    <div
                      key={opp.id}
                      onClick={() => toggleOpportunity(opp.id as OpportunityType)}
                      className={`p-4 rounded-xl border cursor-pointer transition flex items-start gap-3 ${
                        selected
                          ? "bg-indigo-50 border-indigo-300 text-indigo-900 shadow-xs"
                          : "bg-slate-50 border-slate-200 hover:bg-slate-100 text-slate-700"
                      }`}
                    >
                      <input
                        type="checkbox"
                        checked={selected}
                        onChange={() => {}} // Handled by parent div
                        className="mt-1 rounded text-indigo-600 focus:ring-indigo-500"
                      />
                      <div>
                        <h4 className="font-bold text-sm font-display">{opp.label}</h4>
                        <p className="text-xs text-slate-500">{opp.desc}</p>
                      </div>
                    </div>
                  );
                })}
              </div>
            </div>

            {/* Target Discovery Volume Limit Selector */}
            <div className="pt-4 border-t border-slate-100 space-y-3">
              <div className="flex items-center justify-between">
                <label className="block text-xs font-semibold text-slate-700">
                  Discovery Volume Limit (Leads per Campaign Run)
                </label>
                <span className="px-2.5 py-0.5 rounded-full text-xs font-extrabold bg-indigo-100 text-indigo-800">
                  {maxResultsLimit} Leads Target
                </span>
              </div>
              <div className="grid grid-cols-4 gap-3">
                {[20, 50, 100, 200].map((limitVal) => (
                  <button
                    type="button"
                    key={limitVal}
                    onClick={() => setMaxResultsLimit(limitVal)}
                    className={`py-2 px-3 rounded-xl border font-extrabold text-xs transition ${
                      maxResultsLimit === limitVal
                        ? "bg-indigo-600 text-white border-indigo-600 shadow-sm"
                        : "bg-slate-50 border-slate-200 text-slate-700 hover:bg-slate-100"
                    }`}
                  >
                    {limitVal} Leads
                  </button>
                ))}
              </div>
              <p className="text-[11px] text-slate-500">
                Google Places API will paginate using <code className="text-indigo-600">nextPageToken</code> to retrieve up to {maxResultsLimit} leads per run.
              </p>
            </div>

            <div className="pt-4 border-t border-slate-100 space-y-3">
              <label className="block text-xs font-semibold text-slate-700">
                Active Discovery Source Adapters
              </label>
              <div className="flex gap-3 flex-wrap">
                {["google_places", "website_crawler", "social_discovery"].map((source) => (
                  <span
                    key={source}
                    className="px-3 py-1.5 rounded-lg bg-slate-100 border border-slate-200 text-xs font-mono font-medium text-slate-700 flex items-center gap-1.5"
                  >
                    <Globe className="w-3.5 h-3.5 text-indigo-600" />
                    {source}
                  </span>
                ))}
              </div>
            </div>
          </div>
        )}

        {/* STEP 3: Lead Filters */}
        {currentStep === 3 && (
          <div className="space-y-6">
            <div>
              <h2 className="text-lg font-bold text-slate-900 font-display flex items-center gap-2">
                <Users className="w-5 h-5 text-indigo-600" />
                <span>Step 3: Qualification & Demographics Filters</span>
              </h2>
              <p className="text-xs text-slate-500 mt-1">
                Filter target businesses by revenue, headcount, technology stack, and domain keywords.
              </p>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              {/* Revenue */}
              <div className="space-y-2">
                <label className="block text-xs font-semibold text-slate-700 flex items-center gap-1">
                  <DollarSign className="w-3.5 h-3.5 text-emerald-600" /> Annual Revenue Filter ($)
                </label>
                <div className="grid grid-cols-2 gap-3">
                  <input
                    type="number"
                    placeholder="Min Revenue"
                    value={minRevenue}
                    onChange={(e) => setMinRevenue(e.target.value)}
                    className="w-full px-3 py-2 rounded-xl border border-slate-200 bg-slate-50 text-sm text-slate-900 focus:ring-2 focus:ring-indigo-500"
                  />
                  <input
                    type="number"
                    placeholder="Max Revenue"
                    value={maxRevenue}
                    onChange={(e) => setMaxRevenue(e.target.value)}
                    className="w-full px-3 py-2 rounded-xl border border-slate-200 bg-slate-50 text-sm text-slate-900 focus:ring-2 focus:ring-indigo-500"
                  />
                </div>
              </div>

              {/* Employees */}
              <div className="space-y-2">
                <label className="block text-xs font-semibold text-slate-700 flex items-center gap-1">
                  <Users className="w-3.5 h-3.5 text-blue-600" /> Employee Count Filter
                </label>
                <div className="grid grid-cols-2 gap-3">
                  <input
                    type="number"
                    placeholder="Min Employees"
                    value={minEmployees}
                    onChange={(e) => setMinEmployees(e.target.value)}
                    className="w-full px-3 py-2 rounded-xl border border-slate-200 bg-slate-50 text-sm text-slate-900 focus:ring-2 focus:ring-indigo-500"
                  />
                  <input
                    type="number"
                    placeholder="Max Employees"
                    value={maxEmployees}
                    onChange={(e) => setMaxEmployees(e.target.value)}
                    className="w-full px-3 py-2 rounded-xl border border-slate-200 bg-slate-50 text-sm text-slate-900 focus:ring-2 focus:ring-indigo-500"
                  />
                </div>
              </div>
            </div>

            <div className="space-y-4 pt-2">
              <div>
                <label className="block text-xs font-semibold text-slate-700 mb-1 flex items-center gap-1">
                  <Code className="w-3.5 h-3.5 text-purple-600" /> Technology Tags (Comma Separated)
                </label>
                <input
                  type="text"
                  placeholder="e.g. WordPress, React, Shopify"
                  value={technologiesInput}
                  onChange={(e) => setTechnologiesInput(e.target.value)}
                  className="w-full px-4 py-2.5 rounded-xl border border-slate-200 bg-slate-50 text-sm text-slate-900 focus:ring-2 focus:ring-indigo-500"
                />
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-700 mb-1">
                  Domain Keywords (Comma Separated)
                </label>
                <input
                  type="text"
                  placeholder="e.g. commercial, B2B, service"
                  value={keywordsInput}
                  onChange={(e) => setKeywordsInput(e.target.value)}
                  className="w-full px-4 py-2.5 rounded-xl border border-slate-200 bg-slate-50 text-sm text-slate-900 focus:ring-2 focus:ring-indigo-500"
                />
              </div>
            </div>
          </div>
        )}

        {/* STEP 4: Review & Launch */}
        {currentStep === 4 && (
          <div className="space-y-6">
            <div>
              <h2 className="text-lg font-bold text-slate-900 font-display flex items-center gap-2">
                <ShieldCheck className="w-5 h-5 text-indigo-600" />
                <span>Step 4: Final Campaign Review</span>
              </h2>
              <p className="text-xs text-slate-500 mt-1">
                Verify all target parameters before launching your campaign profile.
              </p>
            </div>

            <div className="bg-slate-50 p-6 rounded-2xl border border-slate-200 space-y-4 text-xs text-slate-700">
              <div className="flex justify-between border-b border-slate-200 pb-3">
                <span className="font-semibold text-slate-500">Campaign Title:</span>
                <span className="font-bold text-slate-900 text-sm">{name}</span>
              </div>

              <div className="grid grid-cols-2 gap-4 border-b border-slate-200 pb-3">
                <div>
                  <span className="font-semibold text-slate-500 block">Niche:</span>
                  <span className="font-medium text-slate-900">{niche} {subNiche && `(${subNiche})`}</span>
                </div>
                <div>
                  <span className="font-semibold text-slate-500 block">Geography:</span>
                  <span className="font-medium text-slate-900">{geography}</span>
                </div>
              </div>

              <div className="border-b border-slate-200 pb-3 space-y-1">
                <span className="font-semibold text-slate-500 block">Opportunity Signals:</span>
                <div className="flex gap-1.5 flex-wrap">
                  {opportunityTypes.map((t) => (
                    <span key={t} className="px-2 py-0.5 rounded bg-indigo-100 text-indigo-800 font-medium">
                      {t}
                    </span>
                  ))}
                </div>
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <span className="font-semibold text-slate-500 block">Revenue Bounds:</span>
                  <span>
                    {minRevenue ? `$${minRevenue}` : "No min"} - {maxRevenue ? `$${maxRevenue}` : "No max"}
                  </span>
                </div>
                <div>
                  <span className="font-semibold text-slate-500 block">Headcount Bounds:</span>
                  <span>
                    {minEmployees ? `${minEmployees} emp` : "No min"} - {maxEmployees ? `${maxEmployees} emp` : "No max"}
                  </span>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Wizard Controls */}
        <div className="flex items-center justify-between pt-6 border-t border-slate-100">
          <button
            onClick={handleBack}
            disabled={currentStep === 1 || createMutation.isPending}
            className="flex items-center gap-2 px-4 py-2.5 rounded-xl bg-slate-100 hover:bg-slate-200 text-slate-700 font-semibold text-xs border border-slate-200 transition disabled:opacity-40"
          >
            <ArrowLeft className="w-4 h-4" />
            <span>Back</span>
          </button>

          {currentStep < 4 ? (
            <button
              onClick={handleNext}
              className="flex items-center gap-2 px-5 py-2.5 rounded-xl bg-indigo-600 hover:bg-indigo-700 text-white font-semibold text-xs transition shadow-md shadow-indigo-500/20"
            >
              <span>Continue</span>
              <ArrowRight className="w-4 h-4" />
            </button>
          ) : (
            <button
              onClick={handleSubmit}
              disabled={createMutation.isPending}
              className="flex items-center gap-2 px-6 py-2.5 rounded-xl bg-emerald-600 hover:bg-emerald-700 text-white font-bold text-xs transition shadow-md shadow-emerald-500/20 disabled:opacity-50"
            >
              {createMutation.isPending ? (
                <span>Creating Target...</span>
              ) : (
                <>
                  <Check className="w-4 h-4" />
                  <span>Save & Launch Campaign</span>
                </>
              )}
            </button>
          )}
        </div>
      </div>
    </div>
  );
}
