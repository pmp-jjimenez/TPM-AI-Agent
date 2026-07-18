import { Box, type BoxProps } from '@mui/material';

export function PageContainer(props: BoxProps) {
  return <Box component="section" sx={{ width: '100%', maxWidth: 1200, mx: 'auto' }} {...props} />;
}
