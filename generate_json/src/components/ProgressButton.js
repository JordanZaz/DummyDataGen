import * as React from 'react';
import PropTypes from 'prop-types';
import CircularProgress from '@mui/material/CircularProgress';
import Typography from '@mui/material/Typography';
import Box from '@mui/material/Box';
import LoadingButton from '@mui/lab/LoadingButton';

function CircularProgressWithLabel(props) {
  return (
    <Box sx={{ position: 'relative', display: 'inline-flex' }}>
      <CircularProgress size={30} variant="determinate" {...props} /> {/* Adjust size here */}
      <Box
        sx={{
          top: 0,
          left: 0,
          bottom: 0,
          right: 0,
          position: 'absolute',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
        }}
      >
        <Typography variant="caption" component="div" color="text.secondary">
          {`${Math.round(props.value)}%`}
        </Typography>
      </Box>
    </Box>
  );
}


CircularProgressWithLabel.propTypes = {
  value: PropTypes.number.isRequired,
};

function ProgressButton(props) {
  const [progress, setProgress] = React.useState(10);

  React.useEffect(() => {
    const timer = setInterval(() => {
      setProgress((prevProgress) => (prevProgress >= 100 ? 0 : prevProgress + 10));
    }, 800);
    return () => {
      clearInterval(timer);
    };
  }, []);

  return <CircularProgressWithLabel value={progress} />;
}

export default function GenerateDatasetButton({ loading, ...props }) {
  return (
    <LoadingButton
      loading={loading}
      type="submit"
      variant="contained"
      sx={{ mt: 3, mb: 2 }}
      loadingIndicator={<ProgressButton />}
      {...props}
    >
      Generate Dataset
    </LoadingButton>
  );
}
