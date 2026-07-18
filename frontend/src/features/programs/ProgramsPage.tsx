import { EmptyState } from '../../components/feedback/EmptyState';
import { PageContainer } from '../../components/layout/PageContainer';
import { PageTitle } from '../../components/layout/PageTitle';

export function ProgramsPage() {
  return (
    <PageContainer>
      <PageTitle title="Programs" description="View and manage your program portfolio." />
      <EmptyState
        title="No program data available"
        description="No program data is currently available because backend integration has not yet been implemented. This is an expected application state."
      />
    </PageContainer>
  );
}
