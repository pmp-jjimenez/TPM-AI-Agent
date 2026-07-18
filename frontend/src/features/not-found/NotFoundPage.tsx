import SearchOffOutlinedIcon from '@mui/icons-material/SearchOffOutlined';
import { EmptyState } from '../../components/feedback/EmptyState';
import { PageContainer } from '../../components/layout/PageContainer';
import { PageTitle } from '../../components/layout/PageTitle';

export function NotFoundPage() {
  return (
    <PageContainer>
      <PageTitle title="Page not found" />
      <EmptyState
        icon={<SearchOffOutlinedIcon />}
        title="This page is unavailable"
        description="The requested page does not exist in TPM Operating System."
      />
    </PageContainer>
  );
}
