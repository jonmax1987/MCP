import React, { useState } from 'react';
import {
  Box,
  TextField,
  Button,
  Typography,
  Paper,
  Alert,
  ThemeProvider,
  createTheme,
} from '@mui/material';
import axios from 'axios';

interface CommandHistory {
  id?: string; // ← חדש
  command: string;
  llmResult: any;
  apiResult: any;
  timestamp: string;
  error?: string;
}

const theme = createTheme({
  direction: 'rtl',
  palette: {
    mode: 'light',
    primary: {
      main: '#1976d2',
    },
  },
});

interface MCPInterfaceProps {
  onCommand?: (command: string) => void;
}

interface CommandHistory {
  command: string;
  llmResult: any;
  apiResult: any;
  timestamp: string;
  error?: string;
}

export const MCPInterface: React.FC<MCPInterfaceProps> = ({ onCommand }) => {
  const [command, setCommand] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [history, setHistory] = useState<CommandHistory[]>([]);

  const handleResend = async (id?: string) => {
    if (!id) return;

    setLoading(true);
    setError('');

    try {
      const response = await axios.post(`http://localhost:8001/resend/${id}`);
      const { llm_result, api_result } = response.data;

      setHistory(prev => [
        {
          command: `🔁 ${response.data.original_id}`, // או שים את הטקסט המקורי אם יש
          llmResult: llm_result,
          apiResult: api_result,
          timestamp: new Date().toISOString(),
        },
        ...prev,
      ]);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'שגיאה בשליחה חוזרת');
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!command.trim()) return;

    setLoading(true);
    setError('');

    try {
      const response = await axios.post('http://localhost:8001/command', {
        text: command,
      });

      const { llm_result, api_result } = response.data;

      setHistory(prev => [
        {
          command,
          llmResult: llm_result,
          apiResult: api_result,
          timestamp: new Date().toISOString(),
        },
        ...prev,
      ]);

      if (onCommand) {
        onCommand(command);
      }
    } catch (err: any) {
      setError(err.response?.data?.detail || 'שגיאה ביצירת הבקשה');
      setHistory(prev => [
        {
          command,
          llmResult: null,
          apiResult: null,
          timestamp: new Date().toISOString(),
          error: err.response?.data?.detail || 'שגיאה ביצירת הבקשה',
        },
        ...prev,
      ]);
    } finally {
      setLoading(false);
      setCommand('');
    }
  };

  return (
    <ThemeProvider theme={theme}>
      <Box sx={{ p: 3 }}>
        <form onSubmit={handleSubmit}>
          <Box sx={{ display: 'flex', gap: 2, mb: 3 }}>
            <TextField
              fullWidth
              value={command}
              onChange={(e) => setCommand(e.target.value)}
              placeholder="הכנס פקודה בעברית..."
              variant="outlined"
              size="large"
              disabled={loading}
            />
            <Button
              variant="contained"
              size="large"
              type="submit"
              disabled={loading || !command.trim()}
            >
              שלח
            </Button>
          </Box>

          {error && (
            <Alert severity="error" sx={{ mb: 2 }}>
              {error}
            </Alert>
          )}

          <Paper sx={{ p: 2 }}>
            <Typography variant="h6" gutterBottom>
              היסטוריית פקודות
            </Typography>
            {history.map((item, index) => (
              <Box
                key={index}
                sx={{
                  p: 2,
                  mb: 2,
                  border: '1px solid #eee',
                  borderRadius: 1,
                }}
              >
                <Button
                  variant="outlined"
                  size="small"
                  sx={{ mt: 1 }}
                  onClick={() => handleResend(item.id)}
                  disabled={!item.id}
                >
                  שלח מחדש
                </Button>
                <Typography variant="subtitle1" gutterBottom>
                  {new Date(item.timestamp).toLocaleString('he-IL')}
                </Typography>
                <Typography variant="body1" gutterBottom>
                  פקודה: {item.command}
                </Typography>
                <Typography variant="body2" color="text.secondary" gutterBottom>
                  תוצאה LLM:
                </Typography>
                <pre>{JSON.stringify(item.llmResult, null, 2)}</pre>
                <Typography variant="body2" color="text.secondary" gutterBottom>
                  תוצאה API:
                </Typography>
                <pre>{JSON.stringify(item.apiResult, null, 2)}</pre>
                {item.error && (
                  <Alert severity="error" sx={{ mt: 2 }}>
                    {item.error}
                  </Alert>
                )}
              </Box>
            ))}
          </Paper>
        </form>
      </Box>
    </ThemeProvider>
  );
};
