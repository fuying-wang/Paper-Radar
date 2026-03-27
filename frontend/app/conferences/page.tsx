import SectionPage from "../_components/section-page";

export default function ConferencesPage() {
  return (
    <SectionPage
      title="Conferences"
      description="Conference radar focused on ICLR and related frontier conference topics."
      query="iclr conference openreview"
    />
  );
}
