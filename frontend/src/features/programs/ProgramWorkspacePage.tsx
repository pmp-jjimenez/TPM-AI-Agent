import WorkspacesOutlinedIcon from '@mui/icons-material/WorkspacesOutlined';
import { EmptyState } from '../../components/feedback/EmptyState';
import { PageContainer } from '../../components/layout/PageContainer';
import { PageTitle } from '../../components/layout/PageTitle';

export function ProgramWorkspacePage() {
  return (
    <PageContainer>
      <PageTitle title="Program Workspace" />
      <EmptyState
        icon={<WorkspacesOutlinedIcon />}
        title="Workspace integration pending"
        description="The Program Workspace will become available after backend integration."
      />
    </PageContainer>
  );
}
