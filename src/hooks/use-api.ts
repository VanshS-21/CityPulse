/**
 * API Hooks
 */

import { useQuery, useMutation } from '@tanstack/react-query'

export function useEvents() {
  return useQuery({
    queryKey: ['events'],
    queryFn: async () => ({
      events: [
        {
          id: '1',
          title: 'Test Event',
          category: 'test',
          severity: 'medium',
          status: 'active',
          location: { latitude: 40.7128, longitude: -74.006 },
        },
      ],
    }),
  })
}

export function useCreateEvent() {
  return useMutation({
    mutationFn: async (event: any) => {
      // Mock implementation
      return { id: 'new-event', ...event }
    },
  })
}
