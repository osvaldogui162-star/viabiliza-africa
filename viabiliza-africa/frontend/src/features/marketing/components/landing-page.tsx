"use client";

import { LandingBanksMarquee } from "@/features/marketing/components/landing-banks-marquee";
import { LandingCtaSection } from "@/features/marketing/components/landing-cta-section";
import { LandingFeaturesGrid } from "@/features/marketing/components/landing-features-grid";
import { LandingHeroOfficial } from "@/features/marketing/components/landing-hero-official";
import { LandingProcessSection } from "@/features/marketing/components/landing-process-section";
import { LandingServicesSection } from "@/features/marketing/components/landing-services-section";
import { LandingStatsSection } from "@/features/marketing/components/landing-stats-section";
import { LandingTrustMarquee } from "@/features/marketing/components/landing-trust-marquee";
import { LandingWhyCarousel } from "@/features/marketing/components/landing-why-carousel";
import { MarketingShell } from "@/features/marketing/components/marketing-shell";

export function LandingPage() {
  return (
    <MarketingShell>
      <LandingHeroOfficial />
      <LandingFeaturesGrid />
      <LandingTrustMarquee />
      <LandingStatsSection />
      <LandingServicesSection />
      <LandingProcessSection />
      <LandingWhyCarousel />
      <LandingBanksMarquee />
      <LandingCtaSection />
    </MarketingShell>
  );
}
