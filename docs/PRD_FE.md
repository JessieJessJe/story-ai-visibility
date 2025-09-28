Front End PRD

Tech Stack
This application is built using the following technologies:

Frontend Framework: React with TypeScript
Styling: Tailwind CSS for utility-first styling
Routing: React Router for page navigation
Icons: Lucide React for SVG icons
State Management: React's built-in useState hooks (no external state management library)

Core Features
Text Input

Users can paste blog post content into a text area
The application accepts any text content for analysis
Analysis Process

Content is masked to prevent direct pattern matching
Analysis happens in sequential steps (mask → pillars → questions → models → evaluate)
Progress is visually displayed to the user during analysis
Results Visualization

Overall brand visibility scores by model
Detailed breakdown by "pillars" (brand recognition, value proposition, etc.)
Question-level analysis with model-specific answers
Visual indicators (color-coding) to quickly identify performance levels
Model Comparison

Horizontal bar charts showing overall inference rates by model
Heat map grid showing performance across different pillars
Percentage-based indicators for quick performance assessment

User Flow
User pastes blog post content
User clicks "Analyze" button
System processes content through multiple steps with visual feedback
Results are displayed in a hierarchical format:
Overall model comparison
Pillar-level summaries
Detailed question-level analysis (expandable)

Understanding the Backend API Integration for Brand Visibility Test
Looking at the provided endpoint details, I can see we need to modify the application to work with a specific API structure. Let me walk through how we should adapt the code to match the /analyze endpoint.

Key Changes Needed
API Request Structure:

POST to /analyze endpoint
Send blog text, with optional provider name and aliases
Response Mapping:

Map the response structure to our existing data model
Handle the new structure of "selling_points" (equivalent to our "pillars")
Map "responses" to our current "answers" structure
Progress Indication:

Keep the existing progress simulation since we won't have real-time updates

Proposed Implementation Approach
Based on what I can see, here's how I would implement this:

Create an API client service that handles the request to /analyze
Keep the existing progress simulation UI since we won't have real status updates
Create an adapter function to transform the API response to our existing data model
Update the analyzePost function to use this new API client
Here's a simplified code example of how the analyzePost function might look:

const analyzePost = async (text: string) => {
  if (!text.trim()) return;
  setAnalysisState('loading');
  setCurrentStep('mask');
  setProgress(0);
  
  try {
    // Simulate progress for UI feedback
    simulateProgressSteps();
    
    // Make actual API call
    const response = await apiClient.analyze({
      text: text,
      provider_name: "OpenAI",  // Could be configurable
      provider_aliases: ["Open AI", "ChatGPT"]  // Could be configurable
    });
    
    // Transform API response to our data model
    const result = transformResponseToAnalysisResult(response);
    
    setResult(result);
    setAnalysisState('success');
  } catch (error) {
    console.error('Analysis failed:', error);
    setAnalysisState('error');
  }
};

// Function to simulate progress steps for UI feedback
const simulateProgressSteps = () => {
  const steps = ['mask', 'pillars', 'questions', 'models', 'evaluate'];
  const totalSteps = steps.length;
  
  steps.forEach((step, index) => {
    setTimeout(() => {
      setCurrentStep(step as ProgressStep);
      setProgress(((index + 1) / totalSteps) * 100);
    }, 1000 * (index + 1));
  });
};


```App.tsx
import React, { useState } from 'react';
import { Header } from './components/Header';
import { InputSection } from './components/InputSection';
import { ProgressState } from './components/ProgressState';
import { ResultsSection } from './components/ResultsSection';
import { ErrorState } from './components/ErrorState';
// Analysis state types
type AnalysisState = 'idle' | 'loading' | 'success' | 'error';
type ProgressStep = 'mask' | 'pillars' | 'questions' | 'models' | 'evaluate';
// Mock data types
export interface Question {
  id: string;
  text: string;
  category: string;
  kind: string;
  answers: Answer[];
}
export interface Answer {
  model: string;
  inferred: boolean;
  text: string;
}
export interface Pillar {
  id: string;
  name: string;
  summary: string;
  questions: Question[];
}
export interface AnalysisResult {
  client: string;
  provider: string;
  totalQuestions: number;
  models: string[];
  pillars: Pillar[];
}
export function App() {
  // State
  const [blogText, setBlogText] = useState('');
  const [analysisState, setAnalysisState] = useState<AnalysisState>('idle');
  const [currentStep, setCurrentStep] = useState<ProgressStep>('mask');
  const [progress, setProgress] = useState(0);
  const [result, setResult] = useState<AnalysisResult | null>(null);
  // Mock analysis function
  const analyzePost = async (text: string) => {
    if (!text.trim()) return;
    setAnalysisState('loading');
    setCurrentStep('mask');
    setProgress(0);
    try {
      // Simulate API calls with delays
      await simulateProgress('mask', 20);
      await simulateProgress('pillars', 40);
      await simulateProgress('questions', 60);
      await simulateProgress('models', 80);
      await simulateProgress('evaluate', 100);
      // Set mock result data
      setResult(getMockResult());
      setAnalysisState('success');
    } catch (error) {
      setAnalysisState('error');
    }
  };
  // Helper function to simulate progress steps
  const simulateProgress = async (step: ProgressStep, newProgress: number) => {
    return new Promise<void>(resolve => {
      setTimeout(() => {
        setCurrentStep(step);
        setProgress(newProgress);
        resolve();
      }, 1000); // Each step takes 1 second
    });
  };
  // Retry handler
  const handleRetry = () => {
    setAnalysisState('idle');
  };
  return <div className="min-h-screen bg-gray-50 p-4 md:p-8">
      <div className="max-w-4xl mx-auto">
        <Header />
        <div className="mt-6 space-y-6">
          <InputSection blogText={blogText} setBlogText={setBlogText} onAnalyze={analyzePost} disabled={analysisState === 'loading'} />
          {analysisState === 'loading' && <ProgressState currentStep={currentStep} progress={progress} />}
          {analysisState === 'success' && result && <ResultsSection result={result} />}
          {analysisState === 'error' && <ErrorState onRetry={handleRetry} />}
        </div>
      </div>
    </div>;
}
// Mock data generator
function getMockResult(): AnalysisResult {
  return {
    client: 'Acme Corp',
    provider: 'TechServices Inc',
    totalQuestions: 12,
    models: ['GPT-4', 'Claude', 'Llama'],
    pillars: [{
      id: 'p1',
      name: 'Brand Recognition',
      summary: 'Analysis of how well the brand name and key products are recognized in the content.',
      questions: [{
        id: 'q1',
        text: 'Is the company name mentioned explicitly?',
        category: 'Name Recognition',
        kind: 'Binary',
        answers: [{
          model: 'GPT-4',
          inferred: true,
          text: "Yes, the company name 'Acme Corp' is mentioned 3 times in the blog post."
        }, {
          model: 'Claude',
          inferred: true,
          text: "Yes, 'Acme Corp' appears multiple times throughout the text."
        }, {
          model: 'Llama',
          inferred: false,
          text: "The text refers to a company but doesn't specify Acme Corp by name."
        }]
      }, {
        id: 'q2',
        text: 'Are specific products mentioned by name?',
        category: 'Product Recognition',
        kind: 'List',
        answers: [{
          model: 'GPT-4',
          inferred: true,
          text: 'Yes, the following products are mentioned: AcmeCloud, AcmeSecurity, and AcmeAnalytics.'
        }, {
          model: 'Claude',
          inferred: true,
          text: 'The blog post references AcmeCloud and AcmeSecurity solutions specifically.'
        }, {
          model: 'Llama',
          inferred: true,
          text: 'Products mentioned include cloud services and security solutions from Acme.'
        }]
      }]
    }, {
      id: 'p2',
      name: 'Value Proposition',
      summary: "Evaluation of how clearly the brand's value proposition is communicated.",
      questions: [{
        id: 'q3',
        text: 'What problem does the company solve according to the text?',
        category: 'Problem Statement',
        kind: 'Open',
        answers: [{
          model: 'GPT-4',
          inferred: true,
          text: 'According to the text, Acme Corp solves enterprise-level security challenges while maintaining operational efficiency through their integrated cloud platform.'
        }, {
          model: 'Claude',
          inferred: true,
          text: 'The company addresses security vulnerabilities in cloud infrastructure while simplifying management through a unified dashboard.'
        }, {
          model: 'Llama',
          inferred: false,
          text: "The text doesn't clearly articulate what specific problem is being solved."
        }]
      }]
    }, {
      id: 'p3',
      name: 'Competitive Differentiation',
      summary: 'Assessment of how the brand is positioned against competitors.',
      questions: [{
        id: 'q4',
        text: 'How is the company positioned relative to competitors?',
        category: 'Market Position',
        kind: 'Comparative',
        answers: [{
          model: 'GPT-4',
          inferred: true,
          text: 'Acme Corp is positioned as a premium, enterprise-focused solution with better security features than Competitor X and more comprehensive integration than Competitor Y.'
        }, {
          model: 'Claude',
          inferred: false,
          text: "The blog post doesn't make explicit comparisons to competitors."
        }, {
          model: 'Llama',
          inferred: false,
          text: 'No competitive positioning is evident in the text.'
        }]
      }]
    }]
  };
}
```
```AppRouter.tsx
import React from "react";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import { App } from "./App";
export function AppRouter() {
  return <BrowserRouter>
          <Routes>
            <Route path="/" element={<App />} />
          </Routes>
      </BrowserRouter>;
}
```
```components/ErrorState.tsx
import React from 'react';
import { AlertTriangleIcon } from 'lucide-react';
interface ErrorStateProps {
  onRetry: () => void;
}
export function ErrorState({
  onRetry
}: ErrorStateProps) {
  return <div className="bg-white rounded-lg border border-red-200 shadow-sm p-6">
      <div className="flex items-center gap-3 text-red-600">
        <AlertTriangleIcon size={24} />
        <span className="font-medium">Analysis failed. Please try again.</span>
      </div>
      <button onClick={onRetry} className="mt-4 bg-red-600 hover:bg-red-700 text-white font-medium py-2 px-6 rounded-md transition-colors">
        Retry
      </button>
    </div>;
}
```
```components/Header.tsx
import React from 'react';
export function Header() {
  // For demo purposes, we're setting this to "Dev"
  const environment = 'Dev';
  return <header className="pt-4">
      <div className="flex justify-between items-start">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">
            Brand Visibility Test
          </h1>
          <p className="mt-2 text-gray-600">
            Paste a success-story blog post and analyze brand visibility in
            LLMs.
          </p>
        </div>
        <div className="bg-gray-100 px-3 py-1 rounded-full text-xs font-medium text-gray-800">
          {environment}
        </div>
      </div>
      <div className="h-px bg-gray-200 w-full mt-6"></div>
    </header>;
}
```
```components/InputSection.tsx
import React from 'react';
interface InputSectionProps {
  blogText: string;
  setBlogText: (text: string) => void;
  onAnalyze: (text: string) => void;
  disabled: boolean;
}
export function InputSection({
  blogText,
  setBlogText,
  onAnalyze,
  disabled
}: InputSectionProps) {
  return <div className="bg-white rounded-lg border border-gray-200 shadow-sm p-6">
      <label htmlFor="blog-text" className="block text-sm font-medium text-gray-700 mb-2">
        Blog post text
      </label>
      <textarea id="blog-text" rows={8} className="w-full border border-gray-300 rounded-md shadow-sm px-4 py-3 focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-purple-500 disabled:bg-gray-100 disabled:text-gray-500" placeholder="Paste your blog post content here..." value={blogText} onChange={e => setBlogText(e.target.value)} disabled={disabled} />
      <div className="mt-4 flex flex-col md:flex-row md:justify-between items-start md:items-center">
        <p className="text-xs text-gray-500 mb-3 md:mb-0">
          Content will be masked and analyzed automatically.
        </p>
        <button onClick={() => onAnalyze(blogText)} disabled={disabled || !blogText.trim()} className="w-full md:w-auto bg-purple-600 hover:bg-purple-700 text-white font-medium py-2 px-6 rounded-md disabled:opacity-50 disabled:cursor-not-allowed transition-colors">
          Analyze
        </button>
      </div>
    </div>;
}
```
```components/PillarAccordion.tsx
import React, { useState } from 'react'
import { Pillar } from '../App'
import { QuestionTable } from './QuestionTable'
import { ChevronDownIcon, ChevronUpIcon } from 'lucide-react'
interface PillarAccordionProps {
  pillar: Pillar
}
export function PillarAccordion({ pillar }: PillarAccordionProps) {
  const [isOpen, setIsOpen] = useState(false)
  // Calculate inference rates for this pillar by model
  const modelInferenceRates: Record<
    string,
    {
      inferred: number
      total: number
    }
  > = {}
  // Group answers by model
  pillar.questions.forEach((question) => {
    question.answers.forEach((answer) => {
      if (!modelInferenceRates[answer.model]) {
        modelInferenceRates[answer.model] = {
          inferred: 0,
          total: 0,
        }
      }
      modelInferenceRates[answer.model].total++
      if (answer.inferred) {
        modelInferenceRates[answer.model].inferred++
      }
    })
  })
  // Calculate the overall inference rate for this pillar
  let totalInferred = 0
  let totalAnswers = 0
  Object.values(modelInferenceRates).forEach((stats) => {
    totalInferred += stats.inferred
    totalAnswers += stats.total
  })
  const overallInferenceRate =
    totalAnswers > 0 ? (totalInferred / totalAnswers) * 100 : 0
  return (
    <div className="bg-white rounded-lg border border-gray-200 shadow-sm overflow-hidden">
      <button
        className="w-full text-left px-6 py-4 flex items-center justify-between"
        onClick={() => setIsOpen(!isOpen)}
      >
        <div className="flex items-center">
          <h3 className="font-medium text-gray-900">{pillar.name}</h3>
          <span className="ml-2 inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-gray-100 text-gray-800">
            {pillar.questions.length} questions
          </span>
        </div>
        <div className="flex items-center">
          {/* Inference rate visualization */}
          <div className="mr-4">
            <div className="flex items-center">
              <div className="w-32 h-2 bg-gray-200 rounded-full overflow-hidden mr-2">
                <div
                  className={`h-full ${overallInferenceRate >= 80 ? 'bg-green-500' : overallInferenceRate >= 50 ? 'bg-yellow-500' : 'bg-red-500'}`}
                  style={{
                    width: `${overallInferenceRate}%`,
                  }}
                ></div>
              </div>
              <span className="text-xs font-medium text-gray-700">
                {Math.round(overallInferenceRate)}% inferred
              </span>
            </div>
          </div>
          {isOpen ? (
            <ChevronUpIcon size={18} className="text-gray-500" />
          ) : (
            <ChevronDownIcon size={18} className="text-gray-500" />
          )}
        </div>
      </button>
      {isOpen && (
        <div className="px-6 pb-4">
          <p className="text-gray-600 text-sm mb-4">{pillar.summary}</p>
          <QuestionTable questions={pillar.questions} />
        </div>
      )}
    </div>
  )
}

```
```components/ProgressState.tsx
import React from 'react';
import { EyeOffIcon, ColumnsIcon, HelpCircleIcon, ServerIcon, CheckCircleIcon, LoaderIcon } from 'lucide-react';
type ProgressStep = 'mask' | 'pillars' | 'questions' | 'models' | 'evaluate';
interface ProgressStateProps {
  currentStep: ProgressStep;
  progress: number;
}
interface StepInfo {
  label: string;
  icon: React.ReactNode;
}
export function ProgressState({
  currentStep,
  progress
}: ProgressStateProps) {
  const steps: Record<ProgressStep, StepInfo> = {
    mask: {
      label: 'Mask',
      icon: <EyeOffIcon size={16} />
    },
    pillars: {
      label: 'Pillars',
      icon: <ColumnsIcon size={16} />
    },
    questions: {
      label: 'Questions',
      icon: <HelpCircleIcon size={16} />
    },
    models: {
      label: 'Models',
      icon: <ServerIcon size={16} />
    },
    evaluate: {
      label: 'Evaluate',
      icon: <CheckCircleIcon size={16} />
    }
  };
  const stepKeys = Object.keys(steps) as ProgressStep[];
  return <div className="bg-white rounded-lg border border-gray-200 shadow-sm p-6">
      <div className="flex justify-between mb-4">
        {stepKeys.map(step => {
        const isActive = step === currentStep;
        const isPast = stepKeys.indexOf(step) < stepKeys.indexOf(currentStep);
        return <div key={step} className={`flex flex-col items-center ${isActive ? 'text-purple-600' : isPast ? 'text-gray-500' : 'text-gray-400'}`}>
              <div className={`p-2 rounded-full mb-2 ${isActive ? 'bg-purple-100' : 'bg-gray-100'}`}>
                {steps[step].icon}
              </div>
              <span className="text-xs font-medium">{steps[step].label}</span>
            </div>;
      })}
      </div>
      <div className="w-full bg-gray-200 rounded-full h-2 mb-6">
        <div className="bg-purple-600 h-2 rounded-full transition-all duration-500 ease-out" style={{
        width: `${progress}%`
      }}></div>
      </div>
      <div className="flex items-center justify-center">
        <LoaderIcon size={20} className="text-purple-600 animate-spin mr-2" />
        <span className="text-gray-700">Analyzing blog post...</span>
      </div>
    </div>;
}
```
```components/QuestionTable.tsx
import React from 'react'
import { Question } from '../App'
interface QuestionTableProps {
  questions: Question[]
}
export function QuestionTable({ questions }: QuestionTableProps) {
  return (
    <div className="overflow-x-auto">
      <table className="min-w-full divide-y divide-gray-200">
        <thead className="bg-gray-50">
          <tr>
            <th
              scope="col"
              className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"
            >
              Question
            </th>
            <th
              scope="col"
              className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"
            >
              Category
            </th>
            <th
              scope="col"
              className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"
            >
              Kind
            </th>
            <th
              scope="col"
              className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"
            >
              Answers
            </th>
          </tr>
        </thead>
        <tbody className="bg-white divide-y divide-gray-200">
          {questions.map((question) => (
            <tr key={question.id}>
              <td className="px-6 py-4 whitespace-normal text-sm text-gray-900">
                {question.text}
              </td>
              <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                {question.category}
              </td>
              <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                {question.kind}
              </td>
              <td className="px-6 py-4 whitespace-normal text-sm text-gray-500">
                <div className="grid gap-3">
                  {question.answers.map((answer, index) => (
                    <div
                      key={index}
                      className="border border-gray-200 rounded-md p-3 bg-gray-50"
                    >
                      <div className="flex flex-wrap gap-2 mb-2">
                        <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-gray-200 text-gray-800">
                          {answer.model}
                        </span>
                        {answer.inferred ? (
                          <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800">
                            Provider inferred
                          </span>
                        ) : (
                          <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-red-100 text-red-800">
                            Not inferred
                          </span>
                        )}
                      </div>
                      <p className="text-gray-700">{answer.text}</p>
                    </div>
                  ))}
                </div>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}

```
```components/ResultsSection.tsx
import React from 'react'
import { AnalysisResult } from '../App'
import { PillarAccordion } from './PillarAccordion'
import { ModelComparisonChart } from './ModelComparisonChart'
interface ResultsSectionProps {
  result: AnalysisResult
}
export function ResultsSection({ result }: ResultsSectionProps) {
  return (
    <div className="space-y-4">
      <div className="bg-white rounded-lg border border-gray-200 shadow-sm p-4">
        <div className="flex flex-wrap gap-2">
          <Badge label={`Client: ${result.client}`} />
          <Badge label={`Provider: ${result.provider}`} />
          <Badge label={`${result.totalQuestions} Questions`} />
          <Badge label={`${result.models.length} Models`} />
        </div>
      </div>
      <ModelComparisonChart result={result} />
      <div className="space-y-3">
        {result.pillars.map((pillar) => (
          <PillarAccordion key={pillar.id} pillar={pillar} />
        ))}
      </div>
    </div>
  )
}
function Badge({ label }: { label: string }) {
  return (
    <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-gray-100 text-gray-800">
      {label}
    </span>
  )
}

```
```index.css
/* PLEASE NOTE: THESE TAILWIND IMPORTS SHOULD NEVER BE DELETED */
@import 'tailwindcss/base';
@import 'tailwindcss/components';
@import 'tailwindcss/utilities';
/* DO NOT DELETE THESE TAILWIND IMPORTS, OTHERWISE THE STYLING WILL NOT RENDER AT ALL */
```
```index.tsx
import './index.css';
import React from "react";
import { render } from "react-dom";
import { App } from "./App";
render(<App />, document.getElementById("root"));
```
```tailwind.config.js
export default {
  content: [
    "./src/**/*.{js,jsx,ts,tsx}",
    "./public/index.html",
  ],
  theme: {
    extend: {
      colors: {
        purple: {
          50: '#f6f5ff',
          100: '#edebfe',
          200: '#dcd7fe',
          300: '#cabffd',
          400: '#ac94fa',
          500: '#9061f9',
          600: '#7e3af2',
          700: '#6c2bd9',
          800: '#5521b5',
          900: '#4a1d96',
        }
      }
    },
  },
  plugins: [],
}
```
```components/ModelComparisonChart.tsx
import React from 'react'
import { AnalysisResult, Pillar } from '../App'
interface ModelComparisonChartProps {
  result: AnalysisResult
}
export function ModelComparisonChart({ result }: ModelComparisonChartProps) {
  // Calculate overall inference rates for each model
  const modelStats = result.models.map((model) => {
    let totalAnswers = 0
    let inferredAnswers = 0
    // Calculate total and inferred answers across all pillars
    result.pillars.forEach((pillar) => {
      pillar.questions.forEach((question) => {
        const modelAnswer = question.answers.find(
          (answer) => answer.model === model,
        )
        if (modelAnswer) {
          totalAnswers++
          if (modelAnswer.inferred) inferredAnswers++
        }
      })
    })
    const inferenceRate =
      totalAnswers > 0 ? (inferredAnswers / totalAnswers) * 100 : 0
    return {
      model,
      inferredAnswers,
      totalAnswers,
      inferenceRate,
    }
  })
  // Calculate pillar-specific inference rates for each model
  const pillarStats = result.pillars.map((pillar) => {
    const modelRates: Record<
      string,
      {
        inferred: number
        total: number
        rate: number
      }
    > = {}
    result.models.forEach((model) => {
      let totalAnswers = 0
      let inferredAnswers = 0
      pillar.questions.forEach((question) => {
        const modelAnswer = question.answers.find(
          (answer) => answer.model === model,
        )
        if (modelAnswer) {
          totalAnswers++
          if (modelAnswer.inferred) inferredAnswers++
        }
      })
      const inferenceRate =
        totalAnswers > 0 ? (inferredAnswers / totalAnswers) * 100 : 0
      modelRates[model] = {
        inferred: inferredAnswers,
        total: totalAnswers,
        rate: inferenceRate,
      }
    })
    return {
      pillar,
      modelRates,
    }
  })
  // Helper function to get color based on rate
  const getColorClass = (rate: number) => {
    if (rate >= 80) return 'bg-green-500'
    if (rate >= 50) return 'bg-yellow-500'
    return 'bg-red-500'
  }
  return (
    <div className="bg-white rounded-lg border border-gray-200 shadow-sm p-6">
      <h3 className="text-lg font-medium text-gray-900 mb-4">
        Model Comparison
      </h3>
      {/* Horizontal Bar Chart */}
      <div className="mb-6">
        <h4 className="text-sm font-medium text-gray-700 mb-3">
          Overall Brand Visibility by Model
        </h4>
        <div className="space-y-3">
          {modelStats.map((stat) => (
            <div key={stat.model} className="flex items-center">
              <div className="w-24 text-sm font-medium text-gray-900">
                {stat.model}
              </div>
              <div className="flex-grow">
                <div className="h-6 w-full bg-gray-100 rounded-full overflow-hidden">
                  <div
                    className={`h-full ${getColorClass(stat.inferenceRate)}`}
                    style={{
                      width: `${stat.inferenceRate}%`,
                    }}
                  ></div>
                </div>
              </div>
              <div className="w-16 text-right text-sm font-medium text-gray-700">
                {Math.round(stat.inferenceRate)}%
              </div>
            </div>
          ))}
        </div>
      </div>
      {/* Heat Map Grid */}
      <div>
        <h4 className="text-sm font-medium text-gray-700 mb-3">
          Performance by Pillar
        </h4>
        <div className="overflow-x-auto">
          <table className="min-w-full border-collapse">
            <thead>
              <tr>
                <th className="py-2 px-4 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Pillar
                </th>
                {result.models.map((model) => (
                  <th
                    key={model}
                    className="py-2 px-4 text-center text-xs font-medium text-gray-500 uppercase tracking-wider"
                  >
                    {model}
                  </th>
                ))}
              </tr>
            </thead>
            <tbody>
              {pillarStats.map(({ pillar, modelRates }) => (
                <tr key={pillar.id} className="border-t border-gray-200">
                  <td className="py-2 px-4 text-sm text-gray-900">
                    {pillar.name}
                  </td>
                  {result.models.map((model) => {
                    const stats = modelRates[model]
                    return (
                      <td
                        key={`${pillar.id}-${model}`}
                        className="py-2 px-4 text-center"
                      >
                        <div className="inline-flex items-center justify-center">
                          <div
                            className={`w-8 h-8 rounded-full flex items-center justify-center text-white text-xs font-medium ${getColorClass(stats.rate)}`}
                          >
                            {Math.round(stats.rate)}%
                          </div>
                        </div>
                      </td>
                    )
                  })}
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  )
}

```