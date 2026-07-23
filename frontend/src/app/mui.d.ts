import type { CSSProperties } from 'react';

interface SemanticTone { main: string; subtle: string; border: string; contrastText: string }

declare module '@mui/material/styles' {
  interface TypeBackground { subtle: string }
  interface TypeText { muted: string }
  interface Palette {
    surface: { default: string; elevated: string; sunken: string };
    border: { subtle: string; strong: string };
    status: { healthy: SemanticTone; atRisk: SemanticTone; critical: SemanticTone; informational: SemanticTone; neutral: SemanticTone };
    confidence: { high: SemanticTone; medium: SemanticTone; low: SemanticTone; unknown: SemanticTone };
  }
  interface PaletteOptions {
    surface?: { default: string; elevated: string; sunken: string };
    border?: { subtle: string; strong: string };
    status?: { healthy: SemanticTone; atRisk: SemanticTone; critical: SemanticTone; informational: SemanticTone; neutral: SemanticTone };
    confidence?: { high: SemanticTone; medium: SemanticTone; low: SemanticTone; unknown: SemanticTone };
  }
  interface TypographyVariants {
    pageEyebrow: CSSProperties; pageTitle: CSSProperties; pageSubtitle: CSSProperties;
    sectionTitle: CSSProperties; cardTitle: CSSProperties; metricValue: CSSProperties;
    metricLabel: CSSProperties; supporting: CSSProperties; metadata: CSSProperties;
  }
  interface TypographyVariantsOptions {
    pageEyebrow?: CSSProperties; pageTitle?: CSSProperties; pageSubtitle?: CSSProperties;
    sectionTitle?: CSSProperties; cardTitle?: CSSProperties; metricValue?: CSSProperties;
    metricLabel?: CSSProperties; supporting?: CSSProperties; metadata?: CSSProperties;
  }
}

declare module '@mui/material/Typography' {
  interface TypographyPropsVariantOverrides {
    pageEyebrow: true; pageTitle: true; pageSubtitle: true; sectionTitle: true;
    cardTitle: true; metricValue: true; metricLabel: true; supporting: true; metadata: true;
  }
}

export {};
