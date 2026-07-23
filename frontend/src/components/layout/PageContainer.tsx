import { Box, type BoxProps } from '@mui/material';

export function PageContainer(props: BoxProps) {
  return <Box component="section" sx={{ width: '100%', maxWidth: 1280, mx: 'auto' }} {...props} />;
}
