<!-- cababb76-7805-43bb-8904-2b97220d294b 909138c1-dfc2-4fb2-bc14-97589a9eb20e -->
# Fix Database Schema and Add Captain Selection

## 1. Delete Existing Database Files

Delete the old database files that don't have the `preferredLanes` column:

- `backend/src/db/loldabang.db`
- `backend/dist/db/loldabang.db`

This will force the database to be recreated with the updated schema when the backend starts.

## 2. Add Captain Selection to Balance Page

### Update Balance.vue Interface

Add captain selection state to track which player is selected as captain for each team:

- Add `teamCaptains` ref: `ref<Record<number, number>>({})`  (maps teamIndex -> playerIndex)
- Add captain selection UI in team results

### Update Team Display (lines 89-108)

Modify the team player display to:

- Add captain selection button/icon for each player
- Show crown icon (👑) next to the captain's name
- Add onClick handler to set/unset captain

### Add Captain Selection Functions

```typescript
const selectCaptain = (teamIndex: number, playerIndex: number) => {
  teamCaptains.value[teamIndex] = playerIndex
}

const isCaptain = (teamIndex: number, playerIndex: number): boolean => {
  return teamCaptains.value[teamIndex] === playerIndex
}
```

### Update UI Styling

Add CSS for captain-related elements:

- `.captain-selector` button styling
- `.captain-badge` for crown icon
- Highlight captain row with different background color

## 3. Test the Implementation

- Start backend and frontend
- Create a new match with parsed players (to populate database with preferredLanes)
- Navigate to balance page
- Run balancing
- Click on players to select captains
- Verify captain icon appears and only one captain per team

## Expected Result

- Database recreated with preferredLanes column
- All player data (tier, rank, mainLane, preferredLanes) displays correctly
- Users can click any player in each team to designate them as captain
- Captain shows with crown icon (👑) and highlighted styling

### To-dos

- [ ] Delete backend/src/db/loldabang.db and backend/dist/db/loldabang.db
- [ ] Add teamCaptains ref and captain selection functions to Balance.vue
- [ ] Modify team player display to show captain icon and selection UI
- [ ] Add CSS styling for captain badge and selection buttons
- [ ] Test database recreation, data display, and captain selection