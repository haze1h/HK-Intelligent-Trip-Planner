import type { TravelPlanResponseA } from '../types/travelPlan';

export const mockResponse: TravelPlanResponseA = {
  itinerary: {
    destination: 'Hong Kong',
    days: 2,
    activity_budget_hkd: 3750,
    total_estimated_activity_cost_hkd: 406,
    activities_within_budget: true,
    itinerary: [
      {
        day: 1,
        notes: 'Start with cultural exploration, then move to vibrant street life.',
        morning: {
          activity_name: 'Victoria Peak Morning Hike',
          area: 'The Peak, Hong Kong Island',
          category: 'Nature & Sightseeing',
          estimated_cost_hkd: 0,
          duration_hours: 1.5,
          reason:
            'Free panoramic views of the harbour and skyline during the quieter morning hours.',
        },
        afternoon: {
          activity_name: 'Star Ferry & Tsim Sha Tsui Waterfront',
          area: 'Victoria Harbour',
          category: 'Transport & Sightseeing',
          estimated_cost_hkd: 80,
          duration_hours: 2,
          reason:
            'An iconic and affordable way to cross the harbour with stunning city views.',
        },
        evening: {
          activity_name: 'Temple Street Night Market',
          area: 'Yau Ma Tei, Kowloon',
          category: 'Shopping & Culture',
          estimated_cost_hkd: 100,
          duration_hours: 2,
          reason:
            'Experience local street food, bargain shopping, and lively night atmosphere.',
        },
        daily_cost_hkd: 180,
      },
      {
        day: 2,
        notes: 'Island escape followed by evening city lights.',
        morning: {
          activity_name: 'Lamma Island Hike',
          area: 'Lamma Island',
          category: 'Nature & Adventure',
          estimated_cost_hkd: 46,
          duration_hours: 3,
          reason:
            'A peaceful escape from the city with coastal trails and fresh seafood villages.',
        },
        afternoon: {
          activity_name: 'PMQ & Hollywood Road Art Walk',
          area: 'Central & Sheung Wan',
          category: 'Art & Culture',
          estimated_cost_hkd: 0,
          duration_hours: 2,
          reason:
            'Free galleries, street art, and creative studios in a revitalized heritage building.',
        },
        evening: {
          activity_name: 'Symphony of Lights Show',
          area: 'Tsim Sha Tsui Promenade',
          category: 'Entertainment',
          estimated_cost_hkd: 180,
          duration_hours: 1.5,
          reason:
            'World-famous light and sound show along the harbour skyline, best enjoyed with dinner nearby.',
        },
        daily_cost_hkd: 226,
      },
    ],
    planning_summary:
      'This 2-day Hong Kong itinerary balances free sightseeing with affordable cultural experiences. Day 1 covers iconic landmarks from Victoria Peak to Temple Street Night Market. Day 2 offers a nature escape to Lamma Island followed by art exploration and the famous Symphony of Lights. The total activity cost of HK$406 is well within your HK$3,750 activity budget, leaving plenty of room for spontaneous food discoveries and shopping.',
    budget_context: {
      total_budget_hkd: 6000,
      budget_style: 'standard',
      fixed_cost_estimate_hkd: 2250,
      activity_budget_hkd: 3750,
      fixed_cost_breakdown: {
        accommodation: 1500,
        food: 440,
        transport: 150,
        misc: 160,
      },
      assumptions: [
        'Accommodation: Budget hotel or guesthouse at ~HK$750/night',
        'Food: ~HK$220/day covering local restaurants and street food',
        'Transport: Octopus card with ~HK$75/day for MTR and buses',
        'Miscellaneous: ~HK$80/day for small purchases and emergencies',
      ],
    },
  },
  budget_summary: {
    total_budget_hkd: 6000,
    budget_style: 'standard',
    fixed_cost_estimate_hkd: 2250,
    activity_budget_hkd: 3750,
    activity_total_estimated_cost_hkd: 406,
    total_trip_estimated_cost_hkd: 2656,
    activities_within_budget: true,
    total_trip_within_budget: true,
    activity_over_budget_by_hkd: 0,
    total_over_budget_by_hkd: 0,
    breakdown: {
      activities: 406,
      accommodation: 1500,
      food: 440,
      transport: 150,
      misc: 160,
    },
    assumptions: [
      'Accommodation: Budget hotel or guesthouse at ~HK$750/night',
      'Food: ~HK$220/day covering local restaurants and street food',
      'Transport: Octopus card with ~HK$75/day for MTR and buses',
      'Miscellaneous: ~HK$80/day for small purchases and emergencies',
    ],
    suggestions: [
      'Consider trying dai pai dong (open-air food stalls) for authentic and affordable meals',
      'Use the Airport Express group ticket if traveling with companions',
      'Visit free attractions like Nan Lian Garden or the Avenue of Stars',
      'Buy an Octopus card for seamless public transport payments',
    ],
  },
};
